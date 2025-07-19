from flask import Flask, render_template, url_for, request
from algorithm import *
app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/college-men")
def college_men():
    week_num = request.args.get('week')
    num_weeks = (SEASON_END_POST_NATTIES - SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    teams = filter_teams_without_games(load_teams(f"data/college_mens_ranked_wk{week_num}.json"))
    return render_template('rankings.html', teams=teams, num_weeks=num_weeks)
