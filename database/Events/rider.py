from urllib.error import HTTPError

import firebase_admin
import mongoengine as db

from database.Events import User



from firebase_admin import storage, credentials


class Rider(User):
    stance = db.StringField()
    year_started = db.IntField()
    home_park = db.ReferenceField('Park')
    bib_color = db.StringField()
    registered_contest = db.ListField(db.ReferenceField("Contest"))
    scorecards = db.ListField(db.ReferenceField("Scorecard"))
    statistics = db.ReferenceField('RiderStats')

    @property
    def effort(self):
        # Filter scorecards where landed is False
        failed_scorecards = [s for s in self.scorecards if not s.landed]

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

    def set_image(self, image_path):
        try:
            # Get the storage bucket
            bucket = storage.bucket()

            # Specify the path within the storage bucket
            storage_path = f'Rider/Images/{self.id}'

            # Create a blob in the storage bucket and upload the file
            blob = bucket.blob(storage_path)
            blob.upload_from_filename(image_path)

            # Make the blob publicly accessible
            blob.make_public()

            # Get the public URL
            url = blob.public_url

            # Save the URL to the MongoDB
            self.profile_image = url
            # self.save()
            return self.profile_image

        except Exception as e:
            print(f"Failed to set image for rider: {self.full_name}. Image path: {image_path}")
            print(f"Error: {e}")