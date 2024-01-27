from datetime import datetime
from urllib.error import HTTPError
import mongoengine as db

from Database.user import User


# from google.cloud import storage



class Rider(User):
    stance = db.StringField()
    year_started = db.IntField()
    profile_image = db.StringField(
        default='https://storage.googleapis.com/the-cwa.appspot.com/Rider/Images/default_profile.png')
    home_park = db.ReferenceField('CablePark')
    bib_color = db.StringField()
    board = db.StringField()
    bindings = db.StringField()
    fav_rider = db.StringField()
    fav_trick = db.StringField()
    fav_park = db.StringField()
    instagram = db.StringField()
    youtube = db.StringField()
    facebook = db.StringField()
    bio = db.StringField()
    coach = db.StringField()
    sponsors = db.StringField()
    registered_contest = db.ListField(db.ReferenceField("Contest"))
    scorecard = db.ListField(db.ReferenceField("Scorecard"))
    judge = db.BooleanField(default=False)
    results = db.DynamicField()

    meta = {
        'db_alias': 'test_db'
    }

    @property
    def effort(self):
        # Filter scorecards where landed is False
        failed_scorecards = [s for s in self.scorecard if not s.landed]

        # If there are no such scorecards, return None or a default value
        if not failed_scorecards:
            return None

        # Calculate the sum of difficulty and creativity for these scorecards
        total_difficulty = sum(s.difficulty for s in failed_scorecards)
        total_creativity = sum(s.creativity for s in failed_scorecards)

        # Calculate the average
        num_failed_scorecards = len(failed_scorecards)
        average_effort = (total_difficulty + total_creativity) / (2 * num_failed_scorecards)

        return round(average_effort, 2)

    def register_to_contest(self, contest):
        if contest not in self.registered_contest:
            self.update(push__registered_contest=contest.id)
            self.save()

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
    #     storage_path = f'Rider/Images/{self.id}/{datetime.now()}'
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
    #         self.profile_image = url
    #         # self.save()
    #         return self.profile_image
    #
    #     except HTTPError as e:
    #         if e.code == 429:
    #             print("Too many requests when trying to set the image for rider. Skipping image update.")
    #         else:
    #             print(f"HTTP Error {e.code}: {e.reason}")
    #
    #     except Exception as e:
    #         print(f"Failed to set image for rider: {self.full_name}. Image path: {image_path}")
    #         print(f"Error: {e}")
