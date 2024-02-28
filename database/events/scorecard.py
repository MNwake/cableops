from datetime import datetime

import mongoengine as db


class Scorecard(db.Document):
    date = db.DateTimeField(default=datetime.now)
    section = db.StringField()
    division = db.FloatField()
    execution = db.FloatField()
    creativity = db.FloatField()
    difficulty = db.FloatField()
    score = db.FloatField()
    landed = db.BooleanField()
    park = db.ReferenceField("Park")
    rider = db.ReferenceField("User")
    judge = db.ReferenceField("Judge")

    @classmethod
    def get_scorecards(cls, rider_id=None, sort_by='Most Recent', cursor=None, batch_size=10):
        query_params = {}

        # Filter by rider if rider_id is provided
        if rider_id:
            query_params['rider'] = rider_id

        # Construct the query
        query = cls.objects(**query_params)

        # Apply sorting based on the sort_by parameter
        if sort_by == 'Most Recent':
            query = query.order_by('-date')
        elif sort_by == 'Score: Highest':
            query = query.order_by('-score')
        elif sort_by == 'Score: Lowest':
            query = query.order_by('score')

        # Apply cursor for pagination
        if cursor:
            # Convert cursor to datetime if it's a string
            if isinstance(cursor, str):
                cursor_date = datetime.fromisoformat(cursor)
            else:
                cursor_date = cursor
            query = query.filter(date__lt=cursor_date)

        # Apply batch size limit
        return query.limit(batch_size)

