from datetime import datetime

from firebase_admin import storage
from mongoengine import IntField, StringField, ReferenceField, DateTimeField, BooleanField, FloatField

from database.events import User


class Rider(User):
    stance = StringField()
    year_started = IntField()
    home_park = ReferenceField('Park')
    statistics = ReferenceField('RiderStats')
    division = FloatField()
    is_registered = BooleanField()
    waiver_date = DateTimeField(db_field='waiver_date')
    waiver_url = StringField()

    # meta = {
    #     'collection': 'rider',  # Optional: specify collection name to differentiate from User
    #     'db_alias': 'cable',  # Specifies the alias for the Cable database
    # }

    def set_image(self, image_path, image_type):
        try:
            # Get the storage bucket
            bucket = storage.bucket()

            # Determine the storage path based on image type
            if image_type == 'profile':
                storage_path = f'Rider/ProfileImages/{self.id}'
                attribute = 'profile_image'
            elif image_type == 'waiver':
                storage_path = f'Rider/WaiverImages/{self.id}'
                attribute = 'waiver_url'
            else:
                raise ValueError("Invalid image type specified.")

            # Create a blob in the storage bucket and upload the file
            blob = bucket.blob(storage_path)
            blob.upload_from_filename(image_path)

            # Make the blob publicly accessible
            blob.make_public()

            # Get the public URL and update the appropriate attribute
            url = blob.public_url
            setattr(self, attribute, url)

            # Save the changes to the MongoDB
            self.save()
            return getattr(self, attribute)

        except Exception as e:
            print(f"Failed to set {image_type} image for rider: {self.full_name}. Image path: {image_path}")
            print(f"Error: {e}")

    def to_dict(self):
        """Convert MongoDB document to a dictionary with formatted dates."""
        data = self.to_mongo().to_dict()
        for field in ['date_of_birth', 'date_created', 'waiver_date']:
            if data.get(field):
                data[field] = data[field].strftime("%Y-%m-%dT%H:%M:%S")
        return data

    def update_fields(self, updates: dict):
        exclude_keys = ['date_created', 'division', 'statistics', 'score']
        print('Updating Fields')

        # Convert and validate date fields before updating the object
        for field in ['date_of_birth', 'waiver_date']:
            if field in updates:
                try:
                    # Convert the string to a datetime object
                    updates[field] = datetime.strptime(updates[field], "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    raise ValueError(f"Invalid date format for {updates[field]}")

        for key, value in updates.items():
            if key not in exclude_keys and value is not None and hasattr(self, key):
                # Special handling for home_park
                if key == 'home_park':
                    # Assuming value is the ID of the Park and Park is your model
                    park = Park.objects(id=value).first()
                    if park:
                        print(f"Updating field {key} with Park object")
                        setattr(self, key, park)
                else:
                    print(f"Updating field {key} with value {type(value)}: {value},")
                    setattr(self, key, value)
