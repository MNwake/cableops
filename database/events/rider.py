import mongoengine as db
from firebase_admin import storage

from database.events import User


class Rider(User):
    stance = db.StringField()
    year_started = db.IntField()
    home_park = db.ReferenceField('Park')
    statistics = db.ReferenceField('RiderStats')


    @classmethod
    def get_riders(cls, rider_id=None):
        if rider_id:
            return cls.objects(rider_id=rider_id).all()
        else:
            return cls.objects().all()

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