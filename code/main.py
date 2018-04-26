"""Main application logic
"""
import datetime
import logging
import os

from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_restful import Resource, Api
import MySQLdb
import predictor

import recommender
from event import Event, EventForm
from surveys import UserInterests
from user_class import User

try:
    from google.appengine.api import mail
    from google.appengine.api import app_identity
except ImportError:
    logging.warning('google app engine unable to be imported')

app = Flask(__name__)
app.debug = True

# === APP CONFIGURATIONS
app.config['SECRET_KEY'] = 'secretkey123984392032'

LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(app)

CLOUDSQL_CONNECTION_NAME = os.environ.get('CLOUDSQL_CONNECTION_NAME')
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

DB_HOST_DEV = '35.193.223.145'
ENV_DB = 'Dev'
DB_UNAME = 'kayvon'
DB_PSSWD = 'kayvon'

API = Api(app)
EMAILCONFKEY = '472389hewhuw873dsa4245193ej23yfehw'


def connect_to_cloudsql():
    """Connects to cloud database. When deployed to App Engine,
    the `SERVER_SOFTWARE` environment variable will be set to 'Google App Engine/version'.

    :return: Database connection.
    """
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        database = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    else:
        database = MySQLdb.connect(
            host=DB_HOST_DEV, user=DB_UNAME, passwd=DB_PSSWD, db=ENV_DB, port=3306)

    return database


def query_for_user(user):
    """Queries for information about user from the database.

    :param user: Object User to query for.
    :return: Data about the user.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM Users WHERE username='" + user.username + "'")
    data = cursor.fetchone()
    database.close()
    return data


def authenticate_user(user):
    """Authenticates user password from database.

    :param user: Object User.
    :return: Boolean to authenticate user.
    """
    result = query_for_user(user)
    if result is None:
        return False
    elif result[1] == user.password:
        return True
    return False


def get_user_from_username(user_name):
    """Queries for information about user from the database.

    :param user_name: String username.
    :return: String queried information.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()
    cursor.execute(
        "SELECT username, password, email, fname, lname, dob, timezone, email_verified FROM Users WHERE username='" + user_name + "'")
    data = cursor.fetchone()
    database.close()
    return data


@LOGIN_MANAGER.user_loader
def load_user(user_name):
    """Creates a User class from queried user information.
    :param user_name: String username.
    :return: New User object.
    """
    data = get_user_from_username(user_name)
    if data is None:
        return None
    return User(*data)


def insert_new_user(user):
    """Inserts a new user and its information into the database.

    :param user: Object User.
    :return: None
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()

    query = "INSERT INTO " \
            "Users(username, password, fname, lname, dob, date_joined, timezone, " \
            "email, email_verified) VALUES('{}', '{}', {}, {}, {}, {}, {}, {}, {})".format(
                user.username,
                user.password,
                "'" + user.fname + "'" if user.fname else 'NULL',
                "'" + user.lname + "'" if user.lname else 'NULL',
                "'" + user.dob + "'" if user.dob else 'NULL',
                "'" + str(user.join_date) + "'" if user.join_date else 'NULL',
                "'" + user.timezone + "'" if user.timezone else 'NULL',
                "'" + user.email + "'" if user.email else 'NULL',
                "TRUE" if user.email_verified else "FALSE")

    cursor.execute(query)
    database.commit()
    database.close()


def register_user(user):
    """Checks to see if user is in the database. If not, it will add the user.

    :param user: Object User.
    :return: Boolean for if the user is registered or not.
    """
    if query_for_user(user):
        return False

    insert_new_user(user)
    if query_for_user(user):
        return True


@app.route('/')
def index():
    """Directs web page to home if user is valid in database.

    :return: HTML file for home.
    """
    if current_user.is_authenticated():
        return redirect(url_for('home'))
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Directs web page to registration page to register user.

    :return: HTML file for registration.
    """
    error = None
    if request.method == 'POST':
        try:
            new_user = User(request.form['username'],
                            request.form['password'],
                            request.form['email'],
                            request.form['fname'],
                            request.form['lname'],
                            request.form['dob'],
                            request.form['timezone'],
                            False)
        except ValueError:
            error = 'Username or Password is empty.'

        if register_user(new_user):
            login_user(new_user)
            send_email(new_user.email, new_user.username)
            return redirect(url_for('home'))
        else:
            error = 'Username taken.'

    return render_template('register.html', error=error)


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Directs web page to verification page, and sends verification email.

    :return: HTML file for email verification.
    """
    if request.method == 'POST':
        send_email(current_user.email, current_user.username)
    return render_template('verify_email.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Directs to login page, and logs user in by authenticating user password.

    :return: HTML file for login.
    """
    error = None
    if request.method == 'POST':
        test_user = User(request.form['username'], request.form['password'])

        if authenticate_user(test_user):
            login_user(test_user)
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    """Directs to logout page, and logs user out.

    :return: Function to redirect to homepage.
    """
    logout_user()
    return redirect('/')


@app.route('/home')
@login_required
def home():
    """Directs web page to landing home page depending on user status.

    :return: Function to redirect depending on user status.
    """
    if not current_user.email_verified:
        return redirect('verify')
    if not user_is_tagged(current_user):
        return redirect('survey')
    return redirect(url_for('recommend'))


@app.route('/recommendations')
@login_required
def recommend():
    """Directs web page to user recommendations after authenticating user status.

    :return: HTML file for recommendations.
    """
    if not current_user.email_verified:
        return redirect('verify')
    if not user_is_tagged(current_user):
        return redirect('survey')

    group_id = -1
    g_id = request.args.get('group')
    name = ''
    if g_id is not None:
        group_id = g_id
        name = get_group_by_id(g_id)

    return render_template("recommendations.html", g_id=group_id, name=name)


def helper_strip_date(data):
    """Helper function to rechange the date format.

    :param data: Tuple with event information.
    :return: Tuple with changed date.
    """
    for idx, entry in enumerate(data):
        if isinstance(entry, datetime.datetime):
            data = list(data)
            data[idx] = entry.strftime('%B %d %I:%M %p')
            data = tuple(data)
        if isinstance(entry, datetime.datetime) is str:
            data = list(data)
            data[idx] = unicode(entry, errors='ignore')
            data = tuple(data)
    return data



def purge_user_tags(user):
    """Deletes all user tags from database.

    :param user: User class.
    :return: None.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()

    query = "DELETE FROM UserTags WHERE username='{}'".format(user.username)
    cursor.execute(query)
    database.commit()
    database.close()


def fill_user_tags(user, user_survey):
    """Inserts user tags into database for recommendations from survey.
    :param user: Object User.
    :param user_survey: Object Survey.
    :return: None.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()

    for items in [user_survey.hobbies, user_survey.causes,
                  user_survey.fitness, user_survey.arts_and_culture]:
        for item in items:
            query = "INSERT INTO UserTags(username, tag, category) " \
                                              "VALUES ('{}', '{}', '{}') " \
                                              "ON DUPLICATE KEY UPDATE tag=VALUES(tag), " \
                                              "category=VALUES(category)".format(
                                                  user.username, item, item)
            cursor.execute(query)

    database.commit()
    database.close()


def query_for_survey(user):
    """Queries for user's tags from survey.

    :param user: Object user.
    :return: String data for survey query.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()
    cursor.execute("SELECT * FROM UserTags where username='" + user.username + "'")
    data = cursor.fetchone()
    database.close()
    return data


def user_is_tagged(user):
    """Checks to see if the user has tags.

    :param user: Object User.
    :return: Boolean for user tags.
    """
    result = query_for_survey(user)
    if result is None:
        return False

    return True


@app.route('/survey', methods=['GET', 'POST'])
@login_required
def survey():
    """Directs web page to survey and populates database with user tags from filled survey.

    :return: HTML survey file.
    """
    if not current_user.email_verified:
        return redirect('verify')
    form = UserInterests(request.form)

    if request.method == 'POST' and form.validate():
        survey_obj = UserInterests()
        form.populate_obj(survey_obj)

        purge_user_tags(current_user)
        fill_user_tags(current_user, survey_obj)

        return redirect(url_for('home'))

    return render_template('survey.html', title='Survey', form=form)


@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    """Directs web page to create an event and populates database.

    :return: HTML file for event creation form.
    """
    if not current_user.email_verified:
        return redirect('verify')
    if not user_is_tagged(current_user):
        return redirect('survey')

    form = EventForm(request.form)

    if request.method == 'POST' and form.validate():
        event = EventForm()
        form.populate_obj(event)

        # Create Event form submission
        fill_event(event)

        return redirect(url_for('home'))

    return render_template('create_event.html', title='Create Event', form=form)


def fill_event(event):
    """Populates database for an event.

    :param event: Object Event.
    :return: None.
    """

    database = connect_to_cloudsql()
    cursor = database.cursor()

    # Insert location of event into Locations table
    location_query = "INSERT IGNORE INTO " \
                     "Locations(lname, lat, lon, address_1, address_2, zip, city, state) " \
                     "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                         event.name, event.lat, event.lng,
                         event.formatted_address, event.address_2,
                         event.postal_code, event.sublocality,
                         event.administrative_area_level_1_short)
    cursor.execute(location_query)

    # Get lid of last inserted locatiion, add event to Events table
    lid = cursor.lastrowid
    query = "INSERT INTO Events(ename, description, start_date, end_date, " \
                                      "num_cap, num_attending, lid)" \
                                      " VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                                          event.event_name, event.description,
                                          event.start_date, event.end_date,
                                          event.cap, event.attending, lid)
    cursor.execute(query)

    # Insert category into EventTags
    eid = cursor.lastrowid
    query = "INSERT INTO EventTags(eid, tag, category) " \
                                      "VALUES ('{}', '{}')".format(
                                          eid, event.category)

    database.commit()
    database.close()


def send_email(address, username):
    """Sends email to confirm user.

    :param address: String email address.
    :param username: Object User.
    :return: None.
    """
    confirmation_url = 'gennyc-dev.appspot.com/emailConf/{}/{}'.format(EMAILCONFKEY, username)
    sender_address = (
        'genNYC <support@{}.appspotmail.com>'.format(
            app_identity.get_application_id()))
    subject = 'Confirm your registration'
    body = "Thank you for creating an account!\n\n" \
           "Please confirm your email address by clicking on the link below:" \
           "\n\n{}".format(confirmation_url)
    # print(sender_address, address, subject, body)
    mail.send_mail(sender_address, address, subject, body)


@app.route('/emailConf/<string:key>/<string:username>')
def confirm(key, username):
    """Directs web page based on if user verified their email.

    :param key: Integer random key.
    :param username: String username.
    :return: Redirect function to login page.
    """
    if not key == RANDOM_KEY:
        return redirect(url_for('login'))

    database = connect_to_cloudsql()
    cursor = database.cursor()
    cursor.execute("UPDATE Users SET email_verified=TRUE WHERE username='" +
                   username + "'")
    database.commit()
    database.close()
    logout_user()

    return redirect(url_for('login'))


def get_group_by_id(gid):
    """Gets group information based on group ID.

    :param gid: Group ID.
    :return: String for group information.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()
    query = "SELECT groupName from Groups WHERE gid='" + gid + "'"
    cursor.execute(query)
    data = cursor.fetchone()
    database.close()
    return data[0]


def get_group_names(user):
    """Gets all groups for user.

    :param user: Object User.
    :return: List of groups.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()

    query = "SELECT groupName, status from "  \
            "Groups WHERE username='" + user.username + "'"
    cursor.execute(query)
    data = cursor.fetchall()
    database.close()
    return list((i[0], i[1]) for i in data)



def get_group_members(group_name):
    """Gets all group members for a group.

    :param group_name: String group name.
    :return: List of group members for group.
    """
    database = connect_to_cloudsql()
    cursor = database.cursor()
    query = ("SELECT username, creator, gid from "
             "Groups WHERE groupName='{}'").format(group_name)
    cursor.execute(query)
    data = cursor.fetchall()
    database.close()
    return list(list((i[0], i[1], int(i[2]))) for i in data)


def add_group(group_name, users, new):
    """Populates database for a group and its users.

    :param group_name: String group name.
    :param users: List of users in new group.
    :param new: Boolean for new group.
    :return:
    """
    database = connect_to_cloudsql()
    g_id = 0
    cursor = database.cursor()
    cursor.execute('SELECT max(gid) from Groups')
    data = cursor.fetchone()
    if data[0]:
        g_id = int(data[0])

    if new:
        g_id += 1
        users.append(current_user.username)

    for user in users:
        creator = 0
        status = '2'
        if user == current_user.username:
            status = '1'
            creator = 1
        query = ("INSERT INTO Groups(gid, groupName, username, status, creator) \
        VALUES ('{}','{}','{}','{}','{}')").format(g_id, group_name, user, status, creator)
        cursor.execute(query)
    database.commit()
    database.close()



@app.route('/groups')
@login_required
def group():
    """Directs web page to group and gets user's pending and accepted groups.

    :return: HTML file for groups.
    """
    if not current_user.email_verified:
        return redirect('verify')
    if not user_is_tagged(current_user):
        return redirect('survey')

    groups = get_group_names(current_user)
    pending = {}
    accepted = {}
    for group_name, status in groups:
        members = get_group_members(group_name)
        if status == '1':
            accepted[group_name] = members
        elif status == '2':
            pending[group_name] = members
    username = current_user.username
    return render_template("group.html", pending=pending, accepted=accepted, user=username)


class CreateGroup(Resource):
    """Will create a group.

    The group will consist of users depending on if they have accepted.
    """
    def put(self, groupname, new_flag):
        """Will add a group to the database with its users.

        :param groupname: String group name.
        :param new_flag: Boolean for if the group is being newly created.
        :return: List of group information.
        """
        users = request.args.getlist('users')
        new = True
        if new_flag != 'true':
            new = False
        add_group(groupname, users, new)
        return {}, 200


API.add_resource(CreateGroup, '/api/new_group/<string:groupname>/<string:new_flag>')



class CheckValidUser(Resource):
    """This checks if the user is valid.

    It will connect to the database in order to validate the user.
    """
    def get(self, username):
        """Validates user.

        :param username: String user name.
        :return: List of user information.
        """
        if username == current_user.username:
            return {}, 201
        database = connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("SELECT * FROM Users WHERE username='" + username + "'")
        data = cursor.fetchone()
        database.close()
        if data:
            return {}, 200
        return {}, 201


API.add_resource(CheckValidUser, '/api/validate_username/<string:username>')



class CheckValidUserExisting(Resource):
    """Checks if a user exists.

    It will also check if a user is in the database.
    """
    def get(self, group_name, username):
        """Checks if the user is in the database and in the group.

        :param group_name: String group name.
        :param username: String user name.
        :return: List of user data.
        """
        if username == current_user.username:
            return {}, 201
        database = connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("SELECT * FROM Users WHERE username='" + username + "'")
        data = cursor.fetchone()
        if not data:
            return {}, 201
        cursor.execute(
            "SELECT * FROM Groups WHERE groupName='" +
            group_name + "' AND username='" + username + "'")
        data = cursor.fetchone()
        if data:
            return {}, 201
        return {}, 200


API.add_resource(CheckValidUserExisting,
                 '/api/validate_username/existing/<string:group>/<string:username>')



class CheckValidGroupName(Resource):
    """Checks if a group is valid.

    It also checks if the current user is in a group.
    """
    def get(self, group_name):
        """Gets the current user's group.

        :param group_name: String group name.
        :return: List of groups the user is in.
        """
        if group_name == '':
            return {}, 201
        database = connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute(
            "SELECT * FROM Groups WHERE groupName='" +
            group_name + "' AND username='" + current_user.username + "'")
        data = cursor.fetchone()
        database.close()
        if data:
            return {}, 201
        return {}, 200


API.add_resource(CheckValidGroupName, '/api/validate_groupname/<string:group_name>')



class RespondToRequest(Resource):
    """Updates group information dependeing on user's response.

    If a user rejects/accepts, it will update the pending group invitation.
    """
    def put(self, group_name, response):
        """Updates database according to user's response to invitation.

        :param group_name: String group name.
        :param response: String accept/reject.
        :return: List of responses.
        """
        status = 1
        if response == 'reject':
            status = 3
        database = connect_to_cloudsql()
        cursor = database.cursor()
        cursor.execute("UPDATE Groups SET status='" + str(status) + "' \
        WHERE username='" + current_user.username + "' AND groupName='" + group_name + "'")
        database.commit()
        database.close()
        return {}, 200


API.add_resource(RespondToRequest, '/api/respond_to_request/<string:group_name>/<string:response>')



class GetEventRecs(Resource):
    """Gets event recommendations.

    It will get events based on the current user's interests.
    """
    def get(self):
        """Gets events based on current user's recommendations.

        :return: List of events.
        """
        rec = recommender.Recommend(current_user)
        events = rec.get_events()
        for event_index, event_entry in enumerate(events):
            events[event_index] = helper_strip_date(event_entry)
        response = []
        for event in events:
            event = Event(*event)
            try:
                response.append(event.to_json())
            except:
                continue
        return response


API.add_resource(GetEventRecs, '/api/get_event_recs')



class GetGroupEventRecs(Resource):
    """Gets the group's event recommendations.

    Each group will have recommendations based on each user's interests.

    """
    def get(self, group_id):
        """Gets recommendations for group.

        :param group_id: Integer group ID.
        :return: List of group recommendations.
        """
        rec = recommender.GroupRecommend(group_id)
        events = rec.get_events()
        for event_index, event_entry in enumerate(events):
            events[event_index] = helper_strip_date(event_entry)
        response = []
        for event in events:
            event = Event(*event)
            try:
                response.append(event.to_json())
            except:
                continue
        return response


API.add_resource(GetGroupEventRecs, '/api/get_group_event_recs/<string:group_id>')



class GetGroupInterests(Resource):
    """Gets every user's interest in the group.

    It will then get group's interests after aggregating each user's interest.
    """
    def get(self, group_id):
        """Gets group interests based on every user's interests.

        :param group_id: Integer group ID.
        :return: List of group's interests.
        """
        rec = recommender.GroupRecommend(group_id)
        response = rec.get_group_interests()
        return response


API.add_resource(GetGroupInterests, '/api/get_group_interests/<string:group_id>')


@app.route('/profile')
@login_required
def profile_home():
    """Redirects web page to user's profile.

    :return: Redirect function to user profile.
    """
    return redirect('/profile/' + current_user.username)


@app.route('/profile/<string:username>')
@login_required
def profile(username):
    """Directs web page to user's profile with user's meta information.

    :param username: String username.
    :return: HTML file for user profile.
    """
    data = get_user_from_username(username)
    if data is None:
        return {}, 500
    user = User(*data)
    recommendations = recommender.Recommend(user)

    tags = recommendations.get_user_interests_with_categories()

    return render_template('profile.html', user=user,
                           join_date=db_date_to_normal(user.join_date), tags=tags)

@app.errorhandler(401)
def page_not_found():
    """Directs to error page if user is not logged in.

    :return: HTML file for error page.
    """
    error = 'You must be logged in to view this page.'
    return render_template('error.html', error=error)


def db_date_to_normal(db_date):
    """Normalizes database date.

    :param db_date: Datetime date.
    :return: Datetime new date.
    """
    return db_date.strftime("%B %d, %Y")


if __name__ == '__main__':
    app.run(debug=True)
