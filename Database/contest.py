from datetime import datetime
from urllib.error import HTTPError

import mongoengine as db
# from google.cloud import storage


class Contest(db.Document):
    date_created = db.DateTimeField(default=datetime.now())
    event_name = db.StringField(required=True)
    event_type = db.StringField()
    cost = db.FloatField()
    date = db.DateTimeField()
    image_url = db.StringField(
        default='https://storage.googleapis.com/the-cwa.appspot.com/Contest/Images/64f8007956179a0cc52d8e55/2023-09-06%2001%3A03%3A03.706672')
    start_time = db.DateTimeField()
    location = db.StringField()
    park = db.ReferenceField('CablePark')
    description = db.StringField()
    blog_post = db.StringField()
    hash_tags = db.ListField()
    num_riders_on_water = db.IntField(default=4)
    judges = db.ListField(db.ReferenceField("Judge"))
    registered_riders = db.ListField(db.ReferenceField("Rider"))
    scorecards = db.ListField(db.ReferenceField("Scorecard"))
    completed = db.BooleanField(default=False)
    live = db.BooleanField(default=False)
    results = db.ReferenceField('ContestResults')

    def go_live(self):
        # Set `live` field to False for all other contests
        all_live_contests = Contest.objects(live=True).all()
        for live_contest in all_live_contests:
            if live_contest.live:
                live_contest.live = False
                live_contest.save()

        # Set the current contest to live
        self.live = True

    def remove_duplicate_riders(self):
        unique_riders = list(set(self.registered_riders))
        self.registered_riders = unique_riders
        self.save()  # Save the changes to the database

    def get_ordinal(self, n):
        """Return number with ordinal suffix."""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    @property
    def formatted_date(self):
        if self.date:
            return self.date.strftime('%m/%d/%Y')
        return 'None'

    def formatted_long_date(self):
        if not self.date:
            return None
        month = self.date.strftime('%B').upper()
        day = self.get_ordinal(self.date.day)
        year = self.date.year
        return f"{month} {day} {year}"

    def formatted_day_and_time(self):
        if not self.date:
            return None
        return self.date.strftime('%A, %I:%M%p')

    def register(self, rider):
        if rider not in self.registered_riders:
            self.update(push__registered_riders=rider.id)
            self.save()

    def remove_all_riders(self):
        self.update(set__registered_riders=[])

    @property
    def num_tricks(self):
        """
        Property that returns the number of tricks in the contest.
        """
        return len(self.scorecards)

    @property
    def num_participants(self):
        """
        Property that returns the number of participants in the contest.
        """
        return len(self.registered_riders)

    @property
    def event_card_date(self):
        return self.date.strftime("%b %d") if self.date else ""

    def get_month(self):
        return self.date.strftime("%b")

    def get_day(self):
        return self.date.strftime("%d")

    # def set_image(self, image_path):
    #     # Initialize a storage client
    #     storage_client = storage.Client.from_service_account_json('the-cwa-firebase-adminsdk-dk7pb-09351a6ba0.json')
    #
    #     # Specify the bucket name
    #     bucket_name = 'the-cwa.appspot.com'
    #
    #     # Get the bucket
    #     bucket = storage_client.get_bucket(bucket_name)
    #
    #     # Specify the path within the storage bucket
    #     storage_path = f'Contest/Images/{self.id}/{datetime.now()}'
    #
    #     try:
    #         # Create a blob in the storage bucket and upload the file
    #         blob = bucket.blob(storage_path)
    #         blob.upload_from_filename(image_path)
    #
    #         # Make the blob publicly accessible
    #         blob.make_public()
    #
    #         # Get the public URL
    #         url = blob.public_url
    #
    #         # Save the URL to the MongoDB
    #         self.image_url = url
    #         return 'success', self.image_url
    #
    #     except HTTPError as e:
    #         if e.code == 429:
    #             print("Too many requests when trying to set the image. Skipping image update.")
    #             return "rate_limit_exceeded", None
    #         else:
    #             print(f"HTTP Error {e.code}: {e.reason}")
    #             return "http_error", None
    #     except Exception as e:
    #         print(f"Failed to set image for contest: {self.event_name}. Image path: {image_path}")
    #         print(f"Error: {e}")
    #         return "error", None

    def get_time(self):
        return self.start_time.strftime("%I:%M %p")

    @property
    def formatted_date(self):
        """
        Property that returns the date in 'mm/dd/yyyy' format.
        """
        if self.date:
            return self.date.strftime("%m/%d/%Y")
        else:
            return ""
