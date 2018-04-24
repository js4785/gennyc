import requests
import sys

MEETUP_API_KEY  = '45734f41a137c50167f71323667c68'
MEETUP_API_BASE = 'https://api.meetup.com'

headers = {'Content-Type': 'application/json'}
params = {'key' : MEETUP_API_KEY}

if __name__ == "__main__":
    # category = sys.argv[-1]
    EVENT_URL = sys.argv[-1]
    tmp = EVENT_URL[23:-1].split("/")
    tmp.remove('events')
    URLNAME, EVENT_ID = tmp
    api_url = '{0}/{1}/events/{2}'.format(MEETUP_API_BASE, URLNAME, EVENT_ID)
    r = requests.get(api_url, headers=headers, params=params)
    if r.status_code != 200:
        print (r.headers)
        sys.exit(1)
    f= open("event_info.txt","a")

    try:
        f.write(r.content.decode('utf-8'))
        f.write('\n')
        f.write(EVENT_ID)
        f.write('\n')
        # f.write(category)
        # f.write('\n')
    except:
        print ('error')

    f.close()
    print ('done')
