"""Jobs
"""
# -*- coding: utf-8 -*-
import logging
import os
import datetime
import urllib2
from flask import Flask, redirect
import jinja2
from flask_restful import Resource, Api
import recommender
from user_class import User
import data_retrieval_job as dr
import MySQLdb
from main import connect_to_cloudsql

try:
    from google.appengine.api import mail
    from google.appengine.api import app_identity
    from google.appengine.api import taskqueue
    gae_imported = True
except ImportError:
    logging.warning('google app engine unable to be imported')
    gae_imported = False

if gae_imported:
    if GAE_APP_ID == "gennyc-dev":
        DB_HOST_DEV = '35.193.223.145'
    elif GAE_APP_ID == "gennyc-prod":
        DB_HOST_DEV = '35.225.218.123'
    elif GAE_APP_ID == "gennyc-uat":
        DB_HOST_DEV = '35.225.142.179'
    else:
        raise Exception('invalid project id')
else:
    DB_HOST_DEV = '35.193.223.145'

# DB_HOST_DEV = "127.0.0.1" # Using for local setup

app = Flask(__name__)
app.debug = True

# === APP CONFIGURATIONS

app.config['SECRET_KEY'] = 'secretkey123984392032'

# These environment variables are configured in app.yaml.

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')


ENV_DB = 'Dev'

# print (os.environ.get('BRANCH'))
api = Api(app)
RANDOM_KEY = '472389hewhuw873dsa4245193ej23yfehw'


class PopulateEventsTable(Resource):
    """Populate events table."""

    def get(self, num):
        """Get events."""
        task = taskqueue.add(method='GET', url='/jobs/events/populate/'
                             + num)
        return ('Task {} enqueued, ETA {}.'.format(task.name,
                                                   task.eta), 200)


api.add_resource(PopulateEventsTable,
                 '/jobs/events/trigger_pop_job/<string:num>')


class ExecutePopJob(Resource):
    """Execute population."""

    def get(self, num):
        """Get events added."""
        num = int(num)
        return (dr.add_events_limited(num), 200)


api.add_resource(ExecutePopJob, '/jobs/events/populate/<string:num>')


def req_test():
    """Request test."""
    tomorrow = datetime.date.today()
    url = 'http://www.meetup.com/find/events?allMeetups=true&radius=20 \
           &userFreeform=New+York%2C+NY&mcId=c10001&mcName=New+York \
           %2C+NY&month={}&day={}&year={}'.format(tomorrow.month,
                                                  tomorrow.day,
                                                  tomorrow.year)

    r = r = urllib2.urlopen(url)
    return r.read()


class MailBlastCron(Resource):
    """Mail blast."""

    def get(self):
        """Get mail blast."""
        task = taskqueue.add(method='GET', url='/jobs/mail/blast_all')
        return ('Task {} enqueued, ETA {}.'.format(task.name,
                                                   task.eta), 200)


api.add_resource(MailBlastCron, '/jobs/mail/queue_emails')


class ExecuteMailBlast(Resource):
    """Executes mail blast."""
    def get(self):
        """Get mail blast."""
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('SELECT username, password, email, fname, \
                       lname, dob, timezone, email_verified FROM '
                       + ENV_DB + '.Users')
        rows = cursor.fetchall()
        for row in rows:
            user = User(*row)
            rec = recommender.Recommend(user)
            events = rec.get_events()
            interests = set()
            for e in events:
                interests.add(e[-3])
            for (event_index, e) in enumerate(events):
                events[event_index] = helper_strip_date(e)

            formatted_event_email(user.email, list(interests), events)

            # event_string = ''
            # for eid, ename, desc, start_date, end_date, num_cap, num_attending, lname, add, tag, lat, lon in events:
            #     if (desc is None):
            #         desc = ''
            #     event_string += "{}, {} to {}, {}/{} filled\n{}\n\n".format(ename, start_date, end_date, num_attending, num_cap, desc)
            # print(event_string)
            # body = 'Hey {},\n\nHere are some upcoming events we think you might be interested in:\n\n\n{}'.format(user.fname, event_string)
            # print(user.email)
            # send_events_email(user.email, body)

        return ({}, 200)


api.add_resource(ExecuteMailBlast, '/jobs/mail/blast_all')


def helper_strip_date(e):
    """Format date helper."""
    for (idx, x) in enumerate(e):
        if type(x) is datetime.datetime:
            e = list(e)
            e[idx] = x.strftime('%B %d %I:%M %p')
            e = tuple(e)
    return e


def send_events_email(address, email_body):
    """Send events email."""
    sender_address = \
        'genNYC events <curator@{}.appspotmail.com>'.format(app_identity.get_application_id())
    today = datetime.datetime.now()
    subject = \
        'Weekly event recommendations! - {}/{}'.format(today.month,
                                                       today.day)

    mail.send_mail(sender_address, address, subject, email_body)


def formatted_event_email(address, interests, events):
    """Formatted event email."""
    sender = \
        'genNYC <support@{}.appspotmail.com>'.format(app_identity.get_application_id())
    jinja_environment = \
        jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

    template = \
        jinja_environment.get_template('templates/email_template.html')
    email_body = template.render({'survey_results': interests,
                                  'events': events})

    today = datetime.datetime.now()
    message = mail.EmailMessage(sender=sender,
                                to=address,
                                subject='Weekly event recommendations! - {}/{}'.format(today.month,
                                                                                       today.day),
                                html=email_body)

    message.send()
    return 'OK'


@app.errorhandler(404)
def page_not_found(e):
    """page note found."""
    error = 'page not found'
    print(error)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
