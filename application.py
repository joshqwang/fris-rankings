from flask import Flask, render_template, url_for, request, jsonify
from algorithm import *
application = Flask(__name__)


@application.route("/")
def index():
    return render_template('index.html')

@application.route("/college-men")
def college_men():
    week_num = request.args.get('week')
    num_weeks = (COLLEGE_SEASON_END_POST_NATTIES - COLLEGE_SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    data = {"num_weeks" : num_weeks,
            "division" : "College",
            "gender" : "Men's",
            "url" : "college_mens"}
    return render_template('rankings.html', **data)
@application.route("/college-women")
def college_women():
    week_num = request.args.get('week')
    num_weeks = (COLLEGE_SEASON_END_POST_NATTIES - COLLEGE_SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    data = {"num_weeks" : num_weeks,
            "division" : "College",
            "gender" : "Women's",
            "url" : "college_womens"}
    return render_template('rankings.html', **data)
@application.route("/club-women")
def club_women():
    week_num = request.args.get('week')
    num_weeks = (TODAY - CLUB_SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    #teams = filter_teams_without_games(load_teams(f"data/club_womens_ranked_wk{week_num}.json"))
    data = {"num_weeks" : num_weeks,
            "division" : "Club",
            "gender" : "Women's",
            "url" : "club_womens"}
    return render_template('rankings.html', **data)
@application.route("/club-men")
def club_men():
    week_num = request.args.get('week')
    num_weeks = (TODAY - CLUB_SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    data = {"num_weeks" : num_weeks,
            "division" : "Club",
            "gender" : "Men's",
            "url" : "club_mens"}
    return render_template('rankings.html', **data)

@application.route("/club-mixed")
def club_mixed():
    week_num = request.args.get('week')
    num_weeks = (TODAY - CLUB_SEASON_START).days // 7
    if not week_num:
        week_num = num_weeks
    data = {"num_weeks" : num_weeks,
            "division" : "Club",
            "gender" : "Mixed",
            "url" : "club_mixed"}
    return render_template('rankings.html', **data)

@application.route("/api/rankings/<string:division>/<int:wk_num>")
def get_rankings(division, wk_num):
    teams = filter_teams_without_games(load_teams(f"data/{division}_ranked_wk{wk_num}.json"))
    if "college" in division:
        out = [{
            "rank" : rank + 1,
            "college": team.college,
            "name": team.name,
            "gender": team.gender,
            "rating": team.rating,
        } for rank,team in enumerate(teams)]
    else:
        out = [{
            "rank" : rank + 1,
            "location": team.location,
            "name": team.name,
            "gender": team.gender,
            "rating": team.rating,
        } for rank,team in enumerate(teams)] 
    return jsonify(out)

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production application.
    application.run()