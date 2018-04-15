import urllib2
from bs4 import BeautifulSoup
import requests
import datetime
import sys

def main():
    urls = set()

    today = datetime.date.today()
    tomorrow = today
    for i in range(7):
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
                print(link.get('href'))

    print(len(urls))

if __name__ == "__main__":
    main()
