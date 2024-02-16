from typing import List

import mongoengine as db
from firebase_admin import storage

from database.events import User
from database.utils import calculate_birth_date


class Rider(User):
    stance = db.StringField()
    year_started = db.IntField()
    home_park = db.ReferenceField('Park')
    statistics = db.ReferenceField('RiderStats')


    @classmethod
    def get_riders(cls, home_park_id: str, min_age: int, max_age: int, gender: str,
                   stance: str, year_started: int, rider_id: str, name: str) -> List['Rider']:
        query_params = {}
        
        # Build query parameters
        if home_park_id:
            query_params['home_park'] = home_park_id
        if min_age:
            query_params['date_of_birth__lte'] = calculate_birth_date(min_age)
        if max_age:
            query_params['date_of_birth__gte'] = calculate_birth_date(max_age)
        if gender:
            query_params['gender'] = gender.lower()
        if stance:
            query_params['stance'] = stance.lower()
        if year_started:
            query_params['year_started'] = year_started
        if rider_id:
            query_params['id'] = rider_id
        if name:
            query_params['$or'] = [
                {"first_name__icontains": name.lower()},
                {"last_name__icontains": name.lower()}
            ]
        
        # Execute the query and return filtered riders
        return cls.objects(**query_params)

    @classmethod
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