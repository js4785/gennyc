import requests
import json
import subprocess
import MySQLdb
import datetime
import string
import re
import sys
import os

import urllib2
import urllib
from bs4 import BeautifulSoup
import requests
import predictor


MEETUP_API_KEY  = '45734f41a137c50167f71323667c68'
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
         'yoga', 'sculpting', 'painting', 'museum', 'theater', 'lecture',
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

MEETUP_TAGS = ['arts-culture','beliefs','book-clubs','career-business','dancing',
                'parents-family', 'film','food','hobbies-crafts',
                'education','music','outdoors-adventure','language','sports-fitness',
                'social','tech']
num_events = 200

def get_tagged_events():
    f= open("event_info.txt","w+")
    f.write("")
    f.close()

    for category in MEETUP_TAGS:

        events_added = 0
        days = 5
        while events_added < num_events:

            urls = set()

            today = datetime.date.today()
            tomorrow = today

            tomorrow = tomorrow + datetime.timedelta(days=days)
            # https://www.meetup.com/find/events/arts-culture/?allMeetups=false&radius=5&userFreeform=New+York%2C+NY&mcId=z10025&month=4&day=20&year=2018&eventFilter=all
            url = 'www.meetup.com/find/events/{}/?allMeetups=true&radius=20 \
                  &userFreeform=New+York%2C+NY&mcId=c10001&mcName=New+York%2C+NY \
                  &month={}&day={}&year={}'.format(category, tomorrow.month, tomorrow.day, tomorrow.year)

            r = requests.get('https://' + url)
            print ('https://' + url)
            data = r.text
            soup = BeautifulSoup(data)

            for link in soup.find_all('a'):
                href = link.get('href')
                if ('/events/' in href and '/find/' not in href):
                    urls.add(href)

            print (len(urls))
            if len(urls) == 0:
                break

            for url in urls:
                os.system('python retrieval.py ' + url + ' ' + category)
                events_added += 1
                if events_added > num_events:
                    break

            print ('Finished ' + str(days))
            days += 1

def req_test():
    tomorrow = datetime.date.today()
    url = 'http://www.meetup.com/find/events?allMeetups=true&radius=20&userFreeform=New+York%2C+NY&mcId=c10001&mcName=New+York%2C+NY&month={}&day={}&year={}'.format(tomorrow.month, tomorrow.day, tomorrow.year)
    # return url
    r = r = urllib2.urlopen(url)
    return r.read()

def add_events_limited(day):
    if day != 1 and day != 7:
        return
    db = MySQLdb.connect(host="35.193.223.145",
                     user="kayvon",
                     passwd="kayvon",
                     db="Dev")

    m = predictor.Model()
    urls = set()
    err = 429

    tomorrow = datetime.date.today() + datetime.timedelta(days=day)
    url = 'http://www.meetup.com/find/events?allMeetups=true&radius=20 \
            &userFreeform=New+York%2C+NY&mcId=c10001&mcName=New+York \
            %2C+NY&month={}&day={}&year={}'.format(tomorrow.month, tomorrow.day, tomorrow.year)

    r = urllib2.urlopen(url)
    data = r.read()

    soup = BeautifulSoup(data)

    for link in soup.find_all('a'):
        href = link.get('href')
        if ('/events/' in href and '/find/' not in href):
            urls.add(href)

    added = []
    print len(urls)
    for url in urls:
        tmp = url[23:-1].split("/")
        tmp.remove('events')
        URLNAME, EVENT_ID = tmp
        api_url = '{0}/{1}/events/{2}'.format(MEETUP_API_BASE, URLNAME, EVENT_ID)
        request = urllib2.Request(api_url + '?key=' + MEETUP_API_KEY, headers=headers)
        try:
            result = urllib2.urlopen(request)
        except:
            break
        status = result.getcode()
        if status == err:
            break
        if status != 200:
            continue

        content = result.read()
        event_info = json.loads(content)
        if 'name' in event_info.keys():
            ename = event_info['name']
        else:
            continue
        tag = m.predict_bayes(ename)

        success = add_event_from_info(db, event_info, EVENT_ID, tag)
        if success:
            added.append(ename + ', ' + tag)

    return '\n'.join(added)



def add_events(days):
    # if days < 1 or days > 7:
    #     return
    m = predictor.Model()
    db = MySQLdb.connect(host="35.193.223.145",
                     user="kayvon",
                     passwd="kayvon",
                     db="Dev")


    urls = set()

    today = datetime.date.today()
    tomorrow = today
    tomorrow = tomorrow + datetime.timedelta(days=1)
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
    f= open("event_info.txt","w+")
    f.write("")
    f.close()

    for url in urls:
        os.system('python code/retrieval.py ' + url)

    print ('Finished')


    f = open("event_info.txt","r")
    data = f.read()
    lines = data.split('\n')
    i = 0
    while i < len(lines) - 1:
        if lines[i] == '' or lines[i + 1] == '':
            i += 2
            continue

        event_info = json.loads(lines[i])
        if 'name' in event_info.keys():
            ename = event_info['name']
        else:
            i += 2
            continue
        tag = m.predict_bayes(ename)
        add_event_from_info(db, event_info, lines[i+1], tag)
        i += 2

    f.close()
    db.close()

def add_event_from_info(db, event_info, EVENT_ID, tag):

    if 'description' not in event_info.keys():
        return False

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

    # taglist = []
    # for t in TAGS:
    #     if t in description.lower() or t in ename.lower():
    #         taglist.append(t)
    #
    # if len(taglist) > 0:
    #     print(ename, taglist)
    # else:
    #     return

    cursor = db.cursor()

    cursor.execute("""SELECT eid
                      FROM Events
                      WHERE mid = %s
                    """, (EVENT_ID,))

    result = cursor.fetchone()

    if result:
        print "Event already in database."
        return

    cursor.execute("""SELECT eid
                      FROM Events
                      WHERE ename = %s
                    """, (ename,))
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

    # for tag in taglist:
    # category = None
    # for c in CATEGORIES:
    #     if tag in CATEGORIES[c]:
    #         category = c
    et_query =  """
                INSERT
                INTO EventTags(eid, tag, category)
                VALUES (%s, %s, %s)
                """

    cursor.execute(et_query,( eid,
                              tag,
                              tag))

    db.commit()

    print "Inserted into EventTags."

    if verbose:
        print "Finished."
    return True
