from typing import List

import mongoengine as db
from firebase_admin import storage

from database.events import User, RiderStats


class Rider(User):
    stance = db.StringField()
    year_started = db.IntField()
    home_park = db.ReferenceField('Park')
    statistics = db.ReferenceField('RiderStats')

    @classmethod
    def get_riders(cls, batch_size=50, cursor=None, home_park_id=None, min_age=None, max_age=None, gender=None,
                       stance=None, year_started=None, rider_id=None, name=None):
        query_params = {}

        # Add query parameters based on provided arguments
        if home_park_id is not None:
            query_params['home_park'] = home_park_id
        if min_age is not None:
            query_params['age__gte'] = min_age  # Assuming 'age' field and 'gte' for greater than or equal
        if max_age is not None:
            query_params['age__lte'] = max_age  # Assuming 'age' field and 'lte' for less than or equal
        if gender is not None:
            query_params['gender'] = gender
        if stance is not None:
            query_params['stance'] = stance
        if year_started is not None:
            query_params['year_started'] = year_started
        if rider_id is not None:
            query_params['id'] = rider_id  # Assuming 'id' is the field for rider ID
        if name is not None:
            query_params[
                'name__icontains'] = name  # Assuming 'name' field and 'icontains' for case-insensitive containment

        # Create the initial query with the parameters
        query = cls.objects(**query_params).order_by('id')
        if cursor:
            # Assuming cursor is the ID of the last document in the previous batch
            query = query.filter(id__gt=cursor)
        # Return only the IDs of the riders
        return query.limit(batch_size)

        # If sort_by is not provided, return the result without sorting

    @property
    def division(self):
        # Fetch the latest RiderStats for this rider
        return RiderStats.get_rider_division(self.id)

    @property
    def ranking(self):
        return RiderStats.get_rider_ranking(self.id)

    @property
    def cwa_score(self):
        return RiderStats.get_cwa_score(self.id)

    @property
    def overall_score(self):
        return RiderStats.get_overall_score(self.id)

    @property
    def top_ten_score(self):
        return RiderStats.get_top_ten_score(self.id)

    @property
    def best_trick_score(self):
        return RiderStats.get_best_trick_score(self.id)

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
