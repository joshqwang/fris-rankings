from usau_scraper import *
import re
import requests
from bs4 import BeautifulSoup

INDIVIDUAL_TEAM_BASEURL = "https://play.usaultimate.org/teams/events/Eventteam/"
class Team:
    def __init__(self, college, name, gender, url):
        self.college = college
        self.name = name
        self.gender = gender
        self.url = url
    def __str__(self):
        return f"{self.college} ({self.name})\n{self.gender}'s division\nURL - {self.url}"

# Get a team's schedule for the current season
def fetch_teams(gender_division):
    '''Args = women or men '''
    url = 'https://play.usaultimate.org/teams/events/rankings/'
    teams = {}
    with requests.Session() as req:
        r = req.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        data = {
             "CT_Main_0$btnSubmit" : "Submit",
             'CT_Main_0$F_CompetitionLevelId' : "College",
             'CT_Main_0$F_GenderDivisionId' : ("17" if gender_division == "men" else "2")
                }
        data['__VIEWSTATEGENERATOR'] = soup.find("input", id="__VIEWSTATEGENERATOR").get("value")
        data['__VIEWSTATE'] = soup.find("input", id="__VIEWSTATE").get("value")
        data['__EVENTVALIDATION'] = soup.find("input", id="__EVENTVALIDATION").get("value")
        r = req.post(url, data=data)
        soup = BeautifulSoup(r.content, 'html.parser')
        print_list(get_teams_on_page(soup, "men"))
        del data["CT_Main_0$btnSubmit"] 
        while True:
            next_target = get_next_page(soup, data)
            if not next_target:
                break
            data["__EVENTTARGET"] = next_target

            data['__VIEWSTATEGENERATOR'] = soup.find("input", id="__VIEWSTATEGENERATOR").get("value")
            data['__VIEWSTATE'] = soup.find("input", id="__VIEWSTATE").get("value")
            data['__EVENTVALIDATION'] = soup.find("input", id="__EVENTVALIDATION").get("value")
            r = req.post(url, data=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            print_list(get_teams_on_page(soup, "men"))


def print_list(list):
    for item in list:
        print(item)
def get_teams_on_page(soup, gender):
    teams = []
    for team in soup.find_all(href=re.compile('/teams/events/Eventteam/')):
        url = team['href']
        text_match = re.search("(.*) \((.*)\)", team.text)
        college, name = text_match[1], text_match[2]
        teams.append(Team(college, name, gender, url))
    return teams


    #print(soup.find_all(href=re.compile("/teams/events/Eventteam/")))
def get_next_page(soup, data):
    href = soup.find("a", string=re.compile("Next 20"))
    if not href:
        return None
    return re.search("\('(.*?)'", href['href']).group(1)
fetch_teams("men")