from datetime import datetime, date

import mongoengine as db


class User(db.Document):
    email = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    date_of_birth = db.DateTimeField()
    gender = db.StringField()
    date_created = db.DateTimeField(default=datetime.now())
    profile_image = db.StringField(
        default='https://firebasestorage.googleapis.com/v0/b/the-cwa.appspot.com/o/default-avatar.png?alt=media&token=c069e515-fb20-48eb-847b-b3ef48f58c7e')

    meta = {
        'allow_inheritance': True,  # Allow subclasses to inherit
        'collection': 'user',  # Default collection for User
        'alias': 'default'  # Connects to the main database alias
    }

    class Config:
        from_attributes = True

    @property
    def age(self):
        if not self.date_of_birth:
            return None  # or some default value if date_of_birth is not set

        today = date.today()
        born = self.date_of_birth.date()  # Convert datetime to date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @property
    def age(self):
        if self.date_of_birth is None:
            return 'Unknown'
        else:
            today = datetime.today()
            birth_date = self.date_of_birth
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    @property
    def formatted_dob(self):
        if self.date_of_birth:
            return self.date_of_birth.strftime('%m/%d/%Y')
        return 'None'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def display_name(self):
        return f'{self.first_name[0]}. {self.last_name}'
