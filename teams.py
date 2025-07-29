import datetime
import math
class Game:
    def __init__(self, team_a, a_score, team_b, b_score, date, url):
        self.team_a = team_a
        self.team_b = team_b
        self.a_score = a_score
        self.b_score = b_score
        # Datetime object
        self.date = date
        self.url = url
        # Int. Actually everything else is stored as a string. Probably dumb but whatever.
        # Got to be careful comparing scores, since "13" < "2" but 13 > 2
        self.weight = 1
    def to_dict(self):
        return {
            "team_a": self.team_a.college if self.team_a.college != "" else self.team_a.name,
            "a_score": self.a_score,
            "team_b": self.team_b.college if self.team_b.college != "" else self.team_b.name,
            "b_score": self.b_score,
            "date": self.date.isoformat(),
            "url" : self.url
        }
    @classmethod
    def from_dict(cls, data, team_dict):
        # team_dict must have college keys if division is college, else must be name dict
        team_a = team_dict[data["team_a"]]
        team_b = team_dict[data["team_b"]]
        date = datetime.date.fromisoformat(data['date'])
        return cls(team_a, data["a_score"], team_b, data["b_score"], date, data["url"])
    def __str__(self):
        return f"{self.team_a.name} ({self.a_score}) vs {self.team_b.name} ({self.b_score})"
    def calculate_rating(self):
        r = self.get_losing_score()/(self.get_winning_score() - 1)
        return (125 + 475 * (math.sin(min(1, (1-r)/.5) * 0.4 * math.pi))
                        /math.sin(0.4 * math.pi))
    def get_weight(self, season_start, season_end):
        return self.get_score_weight() * self.get_date_weight(season_start, season_end)
    def get_score_weight(self):
        w = self.get_winning_score()
        l = self.get_losing_score()
        return min(1,
                   math.sqrt((
                       w + max(l, (w-1) // 2)
                   )/19))
    def get_date_weight(self, season_start, season_end):
        season_length = (season_end - season_start).days // 7
        week_num = (self.date - season_start).days // 7
        mult_factor = math.pow(2, 1/season_length)
        return 0.5 * math.pow(mult_factor, week_num)
    def get_winning_score(self):
        return max(int(self.a_score), int(self.b_score))
    def get_losing_score(self):
        return min(int(self.a_score), int(self.b_score))
    def blowout_eligible(self):
        if (self.team_a.rating - self.team_b.rating >= 600 and 
            int(self.a_score) > int(self.b_score) * 2 + 1): 
            return True
        if (self.team_b.rating - self.team_a.rating >= 600 and 
            int(self.b_score) > int(self.a_score) * 2 + 1): 
            return True
        return False
    def forfeited(self):
        return not (self.a_score.isnumeric() and self.b_score.isnumeric())
    def game_won(self):
        return int(self.a_score) > int(self.b_score)
    def game_happened_before_date(self, date):
        return (date - self.date).days > 0



class Team:
    def __init__(self, name, gender, division, url,college="", location=""):
        self.college = college
        self.location = location
        self.division = division
        self.name = name
        self.gender = gender
        self.url = url
        self.rating = 1000
        self.games = []
    def __str__(self):
        newline = '\n'
        return (f"{self.college}{self.location} ({self.name})\n" \
                f"{self.division} {self.gender}'s\n" \
                f"URL - {self.url}\n" \
                f"Games - {[(game.__str__() + newline) for game in self.games]}")
    def to_dict(self):
        if self.division.lower() == "college":
            return {
                "college": self.college,
                "name": self.name,
                "gender": self.gender,
                "division": "college",
                "url": self.url,
                "rating": self.rating,
                "games": [game.to_dict() for game in self.games]
            }
        elif self.division.lower() == "club":
            return {
                "location": self.location,
                "name": self.name,
                "gender": self.gender,
                "division": "club",
                "url": self.url,
                "rating": self.rating,
                "games": [game.to_dict() for game in self.games]   
            }
    @classmethod
    def from_dict(cls, data):
        if data["division"] == "college":
            team = Team(data["name"], data["gender"], data["division"], data["url"], college=data["college"])
        elif data["division"] == "club":
            team = Team(data["name"], data["gender"], data["division"], data["url"], location=data["location"])        
        team.rating = data["rating"]
        # defer loading games until all teams are created
        team._raw_games = data["games"]  # temporary holder
        return team
    def add_game(self, game):
        self.games.append(game)
    def calculate_rating(self, season_start, season_end):
        weights = []
        ratings = []
        total_weight = 0
        new_rating = 0
        for game in self.games:
            if (not game.forfeited() 
                and not game.blowout_eligible()
                and game.game_happened_before_date(season_end)):
                weight = game.get_weight(season_start, season_end)
                rating = game.calculate_rating() if game.game_won() else -1 * game.calculate_rating()
                new_rating += (rating + game.team_b.rating) * weight
                total_weight += weight
        if total_weight == 0:
            return 1000
        return new_rating/total_weight
        