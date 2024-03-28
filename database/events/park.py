import mongoengine as db


class Park(db.Document):
    name = db.StringField(required=True)
    state = db.StringField()
    abbreviation = db.StringField()
    team = db.ReferenceField('Team')
    # cable = db.ListField(db.ReferenceField('Cable'))
    riders_checked_in = db.ListField(db.ReferenceField('Rider'))


    @classmethod
    def get_parks(cls, cursor=None, park_id=None, name=None, state=None, team=None, cable=None, limit=20):
        query_params = {}

        # Add query parameters based on provided arguments
        if park_id is not None:
            query_params['id'] = park_id
        if name is not None:
            query_params['name__icontains'] = name  # Case-insensitive partial match
        if state is not None:
            query_params['state'] = state
        if team is not None:
            query_params['team'] = team
        if cable is not None:
            query_params['cable'] = cable

        # Create the initial query with the parameters
        park_query = cls.objects(**query_params).order_by('id')

        # Apply cursor for pagination
        if cursor:
            park_query = park_query.filter(id__gt=cursor)

        # Return the query results limited by the batch size
        return park_query.limit(limit)

class Team(db.Document):
    name = db.StringField(required=True)
    team_stats = db.ReferenceField('TeamStats')
    riders = db.ListField(db.ReferenceField('Rider'))
