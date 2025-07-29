from scraper import *

def run_one_algorithm_iteration(teams, season_start, season_end):
    # Maps URLs to new rating points
    new_ratings = {}
    for team in teams:
        new_ratings[team.url] = team.calculate_rating(season_start, season_end)
    for team in teams:
        team.rating = new_ratings[team.url]
def filter_teams_without_games(teams):
    return [team for team in teams if team.games]

def run_n_algorithm_iterations(n, in_file, out_file, season_start, season_end):
    teams = load_teams(in_file)
    for i in range(n):
        run_one_algorithm_iteration(teams, season_start, season_end)
    teams.sort(key=lambda team : team.rating, reverse=True)
    save_teams(teams, out_file)

def run_algo_for_all_weeks(n, in_file, out_file_base, season_start, season_end):
    one_week = datetime.timedelta(weeks=1)
    date_runner = season_start + one_week
    week_counter = 0
    while(date_runner < season_end):
        date_runner += one_week
        week_counter += 1
        run_n_algorithm_iterations(n, in_file, f"{out_file_base}_wk{week_counter}.json", season_start, date_runner)

def populate_all_data():
    #run_algo_for_all_weeks(2000, "data/college_mens_unranked.json", "data/college_mens_ranked", COLLEGE_SEASON_START, COLLEGE_SEASON_END_POST_NATTIES)
    #run_algo_for_all_weeks(2000, "data/college_womens_unranked.json", "data/college_womens_ranked", COLLEGE_SEASON_START, COLLEGE_SEASON_END_POST_NATTIES)
    run_algo_for_all_weeks(2000, "data/club_womens_unranked.json", "data/club_womens_ranked", CLUB_SEASON_START, TODAY)
    run_algo_for_all_weeks(2000, "data/club_mens_unranked.json", "data/club_mens_ranked", CLUB_SEASON_START, TODAY)
    run_algo_for_all_weeks(2000, "data/club_mixed_unranked.json", "data/club_mixed_ranked", CLUB_SEASON_START, TODAY)




"""
# TODO:
#   - Blowout detection for teams with less than 5 countable games
#   - Strength of schedule
#   - One JSON file per week
#   - What if? (Change game results)
#   - Website
# """