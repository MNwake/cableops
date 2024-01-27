import certifi
import dns
import mongoengine as db

from Cable.cable import Cable
from Database.contest import Contest
from Database.rider import Rider
from Database.scorecard import Scorecard

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['1.1.1.1']

cable_parks = [{"name": "Terminus Wake Park", "state": "Georgia", "abbreviation": "TERM"},
               {"name": "Orlando Watersports Complex", "state": "Florida", "abbreviation": "OWC"},
               {"name": "Texas Ski Ranch", "state": "Texas", "abbreviation": "TSR"},
               {"name": "KC Watersports", "state": "Kansas", "abbreviation": "KCW"},
               {"name": "Valdosta Wake Compound", "state": "Georgia", "abbreviation": "VWP"},
               {"name": "Elite Cable Park", "state": "Florida", "abbreviation": "ECP"},
               {"name": "Wake Nation Cincinnati", "state": "Ohio", "abbreviation": "WNC"},
               {"name": "Wake Island", "state": "California", "abbreviation": "WIP"},
               {"name": "Next Level Ride", "state": "Texas", "abbreviation": "NLR"},
               {"name": "Hydrous Wake Park", "state": "Texas", "abbreviation": "HYD"}]

cable_park_abbreviations = {
    "Terminus Wake Park": "TERM",
    "Orlando Watersports Complex": "OWC",
    "Texas Ski Ranch": "TSR",
    "KC Watersports": "KCW",
    "Valdosta Wake Compound": "VWP",
    "Elite Cable Park": "ECP",
    "Wake Nation Cincinnati": "WNC",
    "Wake Island": "WIP",
    "Next Level Ride": "NLR",
    "Hydrous Wake Park": "HYD"
}
bib_colors = ['red', 'blue', 'green', 'yellow']
color_dict = {
    "red": [1, 0, 0, 0.2],
    "blue": [0, 0, 1, 0.2],
    "green": [0, 1, 0, 0.2],
    "yellow": [1, 1, 0, 0.2],
    "black": [0, 0, 0, 0.2],
    "orange": [1, 0.5, 0, 0.2],
    "white": [1, 1, 1, 0.2],
}


class DataBase:
    host_name = 'mongodb+srv://events.xfmhxnj.mongodb.net'
    username = 'admin'
    password = 'OGYN9OA6prBilDNK'

    def __init__(self):
        self.archive = None
        try:
            db.connect(db='operations',
                       alias='default',
                       host=self.host_name,
                       username=self.username,
                       password=self.password,
                       tlsCAFile=certifi.where())

            db.connect(db='test',
                       alias='test_db',  # custom alias for test database
                       host=self.host_name,
                       username=self.username,
                       password=self.password,
                       tlsCAFile=certifi.where())

            connection = True


        except Exception as e:
            print(e)


class TheCWA(db.Document):
    mission = 'The Cable Wakeparks Association is a Non-Profit Organization founded by a community of cable wakepark ' \
              'enthusiast. '
    vision = 'We strive to provide access and resources for riders of all levels to learn and enjoy the sport in a ' \
             'safe and inclusive environment. We work to promote the sport at the local and international level, ' \
             'and to create a sense of community and camaraderie among riders and supporters. We are committed to ' \
             'increasing awareness and understanding of cable wakeboarding, and to fostering the growth and ' \
             'development of the sport for the benefit of all. '
    div_labels = {
        (-1, 20): 'Beginner',
        (20, 40): 'Novice',
        (40, 60): 'Intermediate',
        (60, 80): 'Advanced',
        (80, 101): 'Pro'
    }

    @staticmethod
    def average(lst):
        for item in lst:
            if item is None:
                return 0
        if len(lst) == 0:
            return 0
        return sum(lst) / len(lst)

    @staticmethod
    def calculate_division(score):
        for score_range, label in TheCWA.div_labels.items():
            if isinstance(score_range, tuple):
                if score_range[0] <= score < score_range[1]:
                    return label
            elif score == score_range:
                return label

    @property
    def num_riders(self):
        return Rider.objects.count()

    @property
    def num_scorecards(self):
        return Scorecard.objects.count()

    @property
    def num_contests(self):
        return Contest.objects.count()


class CablePark(db.Document):
    name = db.StringField(required=True)
    state = db.StringField(required=True)
    abbreviation = db.StringField(required=True)
    address = db.StringField()
    cable = db.ReferenceField(Cable)
