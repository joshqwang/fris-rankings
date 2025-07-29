import random
import time
from teams import *
import re
import requests
from bs4 import BeautifulSoup
import json

BASEURL = "https://play.usaultimate.org"
INDIVIDUAL_TEAM_BASEURL = "https://play.usaultimate.org/teams/events/Eventteam/"
CURRENT_YEAR = 2025
# The season starts on a Wednesday. This is so tournaments played Friday-Sunday like
# Florida Warmup have the same date weight throughout games
CLUB_SEASON_START = datetime.date.fromisoformat("2025-05-28")

COLLEGE_SEASON_START = datetime.date.fromisoformat("2025-01-01")
COLLEGE_SEASON_END = datetime.date.fromisoformat("2025-05-04")
# This gives Nationals significantly more weight, since it happens far later than any other game.
COLLEGE_SEASON_END_POST_NATTIES = datetime.date.fromisoformat("2025-05-27")
TODAY = datetime.date.today()

def fetch_and_save_all_teams():
    save_teams(fetch_teams("Club", "mixed"), "data/club_mixed_base.json")
    save_teams(fetch_teams("Club", "womens"), "data/club_womens_base.json")
    save_teams(fetch_teams("Club", "mens"), "data/club_mens_base.json")
    save_teams(fetch_teams("College", "mens"), "data/college_mens_base.json")
    save_teams(fetch_teams("College", "womens"), "data/college_womens_base.json")
def populate_all():
    populate_all_teams_from_base("data/club_mens_base.json", "data/club_mens_unranked.json")
    populate_all_teams_from_base("data/club_womens_base.json", "data/club_womens_unranked.json")
    populate_all_teams_from_base("data/club_mixed_base.json", "data/club_mixed_unranked.json")
    populate_all_teams_from_base("data/college_mens_base.json", "data/college_mens_unranked.json")
    populate_all_teams_from_base("data/college_womens_base.json", "data/college_womens_unranked.json")

def partial_population_all():
    partial_population("data/club_mens_base.json", "data/club_mens_unranked.json")
    partial_population("data/club_womens_base.json", "data/club_womens_unranked.json")
    partial_population("data/club_mixed_base.json", "data/club_mixed_unranked.json")
    partial_population("data/college_mens_base.json", "data/college_mens_unranked.json")
    partial_population("data/college_womens_base.json", "data/college_womens_unranked.json")


# Get a team's schedule for the current season
def fetch_teams(division, gender):
    '''Args = women or men '''
    url = 'https://play.usaultimate.org/teams/events/rankings/'
    teams = []
    with requests.Session() as req:
        r = req.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        data = {
             "CT_Main_0$btnSubmit" : "Submit",
             'CT_Main_0$F_CompetitionLevelId' : division,
             'CT_Main_0$F_GenderDivisionId' : ("17" if gender == "mens" else "2" if gender == "womens" else "1")
                }
        data['__VIEWSTATEGENERATOR'] = soup.find("input", id="__VIEWSTATEGENERATOR").get("value")
        data['__VIEWSTATE'] = soup.find("input", id="__VIEWSTATE").get("value")
        data['__EVENTVALIDATION'] = soup.find("input", id="__EVENTVALIDATION").get("value")
        r = req.post(url, data=data)
        soup = BeautifulSoup(r.content, 'html.parser')
        teams += get_teams_on_page(soup, gender, division)
        del data["CT_Main_0$btnSubmit"] 
        while True:
            next_target = get_next_page(soup)
            if not next_target:
                break
            data["__EVENTTARGET"] = next_target

            data['__VIEWSTATEGENERATOR'] = soup.find("input", id="__VIEWSTATEGENERATOR").get("value")
            data['__VIEWSTATE'] = soup.find("input", id="__VIEWSTATE").get("value")
            data['__EVENTVALIDATION'] = soup.find("input", id="__EVENTVALIDATION").get("value")
            r = req.post(url, data=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            teams += get_teams_on_page(soup, gender, division)
    return teams
# For debugging purposes
def print_list(list):
    for item in list:
        print(item)
# Takes a soup and a gender_division, returns a list of Team objects
def get_teams_on_page(soup, gender, division):
    teams = []
    for row in soup.find_all(lambda tag : tag.name == "tr" and tag.find(href=re.compile('/teams/events/Eventteam/'))):
        team = row.find(href=re.compile('/teams/events/Eventteam/'))
        url = team['href']
        if division.lower() == "college":
            text_match = re.search("(.*) \((.*)\)", team.text)
            college, name = text_match[1], text_match[2]
            teams.append(Team(name, gender, "college", url, college=college))
        elif division.lower() == "club":
            teams.append(Team(team.text, gender, "club", url, location=row.contents[-3].text))
    return teams

# Takes a soup and returns the event target string.
def get_next_page(soup):
    href = soup.find("a", string=re.compile("Next"))
    if not href:
        return None
    return re.search("\('(.*?)'", href['href']).group(1)

# Saves a list of Team objects into a file
def save_teams(teams, filename):
    with open(filename, "w") as f:
        json.dump([team.to_dict() for team in teams], f, indent=4)

# Loads a list of Team objects from a file
def load_teams(filename):
    with open(filename) as f:
        teams_raw = json.load(f)

    teams = [Team.from_dict(data) for data in teams_raw]
    if teams[0].division.lower() == "college":
        team_dict = {team.college: team for team in teams}
    if teams[0].division.lower() == "club":
        team_dict = {team.name: team for team in teams}
    for team in teams:
        # Populate games
        team.games = [Game.from_dict(g, team_dict) for g in team._raw_games]
        del team._raw_games  # cleanup
    return teams

# Takes a Team object and a url dict and scrapes USAU to populate their results
def populate_team_results(team, team_dict):
    # Requires team_dict to be a url dict mapping urls to teams
    with requests.Session() as req:
        r = req.get(BASEURL + team.url)
        while not r.ok:
            print("request failed, retrying")
            # Retry request if request fails
            time.sleep(random.randint(0, 3)) 
            r = req.get(BASEURL + team.url)
        soup = BeautifulSoup(r.content, 'html.parser')
    scheduleTable = soup.find(id="CT_Right_0_gvEventScheduleScores")
    if not scheduleTable:
        # No games found
        return
    rows = scheduleTable.find_all("tr")
    for row in rows:
        try:
            date_str = row.find(id=re.compile("CT_Right_0_gvEventScheduleScores_ctl.*_lblMonth")).text
            date = datetime.datetime.strptime(f"{date_str} {CURRENT_YEAR}", "%B %d %Y").date()
            results = row.find_all("a")
            score, opponent = results
            url = score.get("href")
            score = score.text
            opponent = opponent['href']
            team_score, _, opp_score = score.split()
            team.add_game(Game(team, team_score, team_dict[opponent], opp_score, date, url))
        except Exception as e:
            print("exception hit", e)
            continue
         


#save_teams(fetch_teams("men"), "teams_base.json")
def populate_all_teams_from_base(in_filename, out_filename):
    teams = load_teams(in_filename)
    team_url_dict = {team.url: team for team in teams}
    for team in teams:
        if not team.games:
            time.sleep(random.randint(0, 3)) 
            print("Populating team ", team.name)
            populate_team_results(team, team_url_dict)
    save_teams(teams, out_filename)
# For debugging purposes
def partial_population(in_filename, out_filename):
    teams = load_teams(in_filename)
    team_url_dict = {team.url: team for team in teams}
    for team in teams[:5]:
        if not team.games:
            time.sleep(random.randint(0, 3)) 
            print("Populating team ", team.name)
            populate_team_results(team, team_url_dict)
    save_teams(teams, out_filename)
