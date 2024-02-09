import base64
import hashlib
import hmac
import time
from datetime import datetime, date, timedelta
import mongoengine as db


class User(db.Document):
    email = db.StringField()
    password = db.StringField()
    first_name = db.StringField(required=True)
    last_name = db.StringField(required=True)
    date_of_birth = db.DateTimeField()
    gender = db.StringField()
    date_created = db.DateTimeField(default=datetime.utcnow)
    token = db.StringField()
    token_expiration = db.DateTimeField()
    profile_image = db.StringField(
        default='https://storage.googleapis.com/the-cwa.appspot.com/Rider/Images/default_profile.png')

    meta = {'allow_inheritance': True}

    @property
    def age(self):
        if not self.date_of_birth:
            return None  # or some default value if date_of_birth is not set

        today = date.today()
        born = self.date_of_birth.date()  # Convert datetime to date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def generate_token(self):
        """Generates a token."""
        secret_key = 'I42JS0ltca2'
        # Get the current timestamp.
        timestamp = str(time.time())
        # Create a string that consists of the user ID and the current timestamp.
        data = f"{str(self.id)}:{timestamp}"
        # Create a signature by hashing the data with the secret key.
        signature = hashlib.sha256((data + secret_key).encode()).hexdigest()
        # The token consists of the data and the signature.
        token = f"{data}:{signature}"
        # Encode the token in Base64.
        token = base64.b64encode(token.encode()).decode()
        self.token = token
        self.token_expiration = datetime.utcnow() + timedelta(hours=1)
        self.save()  # Update user's token and token_expiration fields
        return token

    @staticmethod
    def verify_token(token):
        """Verifies a token."""
        secret_key = 'I42JS0ltca2'
        # Decode the token from Base64.
        token = base64.b64decode(token.encode()).decode()
        # Split the token into the data and the signature.
        data, signature = token.rsplit(":", 1)
        # Check if the signature is correct.
        expected_signature = hashlib.sha256((data + secret_key).encode()).hexdigest()
        if hmac.compare_digest(expected_signature, signature):
            # The token is valid, return the user ID.
            user_id, timestamp = data.split(":")
            return User.objects(id=user_id).first() if User.objects(id=user_id) else None
        else:
            # The token is invalid.
            return None

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

    @classmethod
    def all_judges(cls):
        return cls.objects(judge=True)
