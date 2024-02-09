import mongoengine as db

from database.Events import Rider, Scorecard, Contest


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

