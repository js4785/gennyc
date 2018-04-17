import requests
import json
import subprocess
import MySQLdb
import datetime
import string
import re

import urllib2
from bs4 import BeautifulSoup
import requests

MEETUP_API_KEY  = '6e735a762056651032171a3d106b4d78'
MEETUP_API_BASE = 'https://api.meetup.com'

URL_RE  = r'^https?:\/\/.*[\r\n]*'
TAG_RE = r'</?([a-z][a-z0-9]*)\b[^>]*>'

CATEGORY_LIMIT = 20
MIN_CHARS_DESC = 200
TAG_LENGTH_LIMIT = 100

headers = {'Content-Type': 'application/json'}
params = {'key' : MEETUP_API_KEY}

verbose = True

TAGS = [ 'desserts', 'wine', 'beer', 'vegetarian', 'vegan', 'meats', 'bbq',
         'tapas', 'brunch', 'romantic', 'trendy', 'diy', 'soccer', 'football',
         'basketball', 'baseball', 'tennis', 'lacrosse', 'hockey', 'golf',
         'indoors', 'outdoors', 'water', 'adrenaline', 'dance', 'pilates', 'boxing',
         'yoga', 'spin', 'sculpting', 'painting', 'museum', 'theater', 'lecture',
         'learn', 'clubbing', 'pop', 'karaoke'
        ]
CATEGORIES = {'food_drink': ['desserts', 'wine', 'beer', 'vegetarian', 'vegan', 'meats', 'bbq',
              'tapas', 'brunch', 'romantic', 'trendy', 'diy'],
              'sports': ['soccer', 'football',
              'basketball', 'baseball', 'tennis', 'lacrosse', 'hockey', 'golf'],
              'location': ['indoors', 'outdoors', 'water'],
              'fitness': ['dance', 'pilates', 'boxing','yoga', 'spin', 'sculpting'],
              'arts_culture': ['painting', 'museum', 'theater', 'lecture', 'learn'],
              'music': ['clubbing', 'pop', 'karaoke']
             }

def add_events(days):
    if days < 1 or days > 7:
        return

    db = MySQLdb.connect(host="35.193.223.145",
                     user="kayvon",
                     passwd="kayvon",
                     db="Dev")


    urls = set()

    today = datetime.date.today()
    tomorrow = today
    for i in range(days):
        tomorrow = tomorrow + datetime.timedelta(days=1)
        url = 'www.meetup.com/find/events/?allMeetups=true&radius=20 \
              &userFreeform=New+York%2C+NY&mcId=c10001&mcName=New+York%2C+NY \
              &month={}&day={}&year={}'.format(tomorrow.month, tomorrow.day, tomorrow.year)

        r = requests.get('https://' + url)
        data = r.text
        soup = BeautifulSoup(data)

        for link in soup.find_all('a'):
            href = link.get('href')
            if ('/events/' in href and '/find/' not in href):
                urls.add(href)

    print (len(urls))
    for url in urls:
        print (url)
        add_event_from_url(db, url)

    db.close()

def add_event_from_url(db, url):
    EVENT_URL = url

    tmp = EVENT_URL[23:-1].split("/")
    tmp.remove('events')

    URLNAME, EVENT_ID = tmp

    api_url = '{0}/{1}/events/{2}'.format(MEETUP_API_BASE, URLNAME, EVENT_ID)

    r = requests.get(api_url, headers=headers, params=params)

    if r.status_code == 200:
        # event information
        pass
    else:
        if verbose:
            print (r.status_code)
            print "Get event failed"
        return

    event_info = json.loads(r.content.decode('utf-8'))

    if len(event_info['description']) < MIN_CHARS_DESC:
        if verbose:
            print "Failure: event description too short (>={} chars needed)".format(MIN_CHARS_DESC)
        return

    if 'name' in event_info.keys():
        ename = event_info['name']
    else:
        ename = None

    if 'venue' in event_info.keys():
        if 'name' in event_info['venue'].keys() and event_info['venue']['name']:
            lname = event_info['venue']['name']
        else:
            lname = None

        if 'lon' in event_info['venue'].keys() and event_info['venue']['lon']:
            lon = event_info['venue']['lon']
        else:
            lon = None

        if 'lat' in event_info['venue'].keys() and event_info['venue']['lat']:
            lat = event_info['venue']['lat']
        else:
            lat = None

        if 'address_1' in event_info['venue'].keys() and event_info['venue']['address_1']:
            address_1 = event_info['venue']['address_1']
        else:
            address_1 = None

        if 'zip' in event_info['venue'].keys() and event_info['venue']['zip']:
            zip = event_info['venue']['zip']
        else:
            zip = None

        if 'city' in event_info['venue'].keys() and event_info['venue']['city']:
            city = event_info['venue']['city']
        else:
            city = None

        if 'state' in event_info['venue'].keys() and event_info['venue']['state']:
            state = event_info['venue']['state']
        else:
            state = None
    else:
        lname = lon = lat = address_1 = zip = city = state = None

    if 'time' in event_info.keys() and event_info['time']:
        start_time = event_info['time']
    else:
        start_time = None

    if 'duration' in event_info.keys() and event_info['duration']:
        duration = event_info['duration']
    else:
        duration = None

    if 'description' in event_info.keys() and event_info['description']:
        description = event_info['description']
    else:
        description = None

    taglist = []
    for t in TAGS:
        if t in description.lower() or t in ename.lower():
            taglist.append(t)

    if len(taglist) > 0:
        print(ename, taglist)
    else:
        return

    cursor = db.cursor()

    cursor.execute("""SELECT eid
                      FROM Events
                      WHERE mid = %s
                    """, (EVENT_ID,))

    result = cursor.fetchone()

    if result:
        print "Event already in database."
        return

    loc_query = """
                INSERT
                INTO Locations(lname, lat, lon, address_1, zip, city, state)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

    cursor.execute(loc_query, ( lname,
                                lon,
                                lat,
                                address_1,
                                zip,
                                city,
                                state))

    db.commit()

    print "Inserted into Locations."

    cursor.execute("SELECT LAST_INSERT_ID()")

    lid = cursor.fetchone()

    start_date = str(datetime.datetime.fromtimestamp(start_time / 1000))

    if start_date and duration:
        end_date = str(datetime.datetime.fromtimestamp((start_time + duration) / 1000))
    else:
        end_date = None

    ev_query =  """
                INSERT
                INTO Events(ename, start_date, end_date,
                            num_attending, lid, description, mid)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """

    cursor.execute(ev_query,   (ename.encode('ascii', 'ignore'),
                                start_date,
                                end_date,
                                0,
                                lid,
                                description.encode('ascii', 'ignore'),
                                EVENT_ID))

    db.commit()

    print "Inserted into Events."

    cursor.execute("SELECT LAST_INSERT_ID()")

    eid = cursor.fetchone()

    for tag in taglist:
        category = None
        for c in CATEGORIES:
            if tag in CATEGORIES[c]:
                category = c
        et_query =  """
                    INSERT
                    INTO EventTags(eid, tag, category)
                    VALUES (%s, %s, %s)
                    """

        cursor.execute(et_query,( eid,
                                  tag,
                                  category))

    db.commit()

    print "Inserted into EventTags."

    if verbose:
        print "Finished."
