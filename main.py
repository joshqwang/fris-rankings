from usau_scraper import *
import requests
from bs4 import BeautifulSoup

# Get a team's basic information


# Get a team's schedule for the current season
def fetch_teams(gender_division):
    '''Args = Women or Men '''
    url = 'https://play.usaultimate.org/teams/events/rankings/'
    teams = {}
    with requests.Session() as req:
        r = req.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        data = {
             "__EVENTTARGET": "CT_Main_0$gvList$ctl23$ctl00$ctl00",
             'CT_Main_0$F_CompetitionLevelId' : "College"
                }
        data['__VIEWSTATEGENERATOR'] = soup.find("input", id="__VIEWSTATEGENERATOR").get("value")
        data['__VIEWSTATE'] = soup.find("input", id="__VIEWSTATE").get("value")
        data['__EVENTVALIDATION'] = soup.find("input", id="__EVENTVALIDATION").get("value")
        r = req.post(url, data=data)
        soup = BeautifulSoup(r.content, 'html.parser')
        print(data)
        print(soup.prettify())

def generate_data(req):

    r = req.get('https://play.usaultimate.org/teams/events/rankings/')
    soup = BeautifulSoup(r.content, 'html.parser')


    return data
fetch_teams("Men")