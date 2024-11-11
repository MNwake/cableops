from typing import List, Optional
from pydantic import BaseModel, validator
from bson import ObjectId
from database.cable.park import Park

from pydantic import BaseModel


class CableBase(BaseModel):
    id: str
    name: str
    num_carriers: int  # Following snake_case for JSON mapping

    class Config:
        orm_mode = True
        from_attributes = True


class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class ContactBase(BaseModel):
    phone_number: str
    name: str
    position: str
    email: str

    class Config:
        orm_mode = True
        from_attributes = True


class ParkBase(BaseModel):
    id: str
    name: str
    abbreviation: Optional[str] = None
    cover_photo: Optional[str] = None
    logo: Optional[str] = None
    address: Optional[AddressBase] = None
    maintenance: Optional[str] = None
    contacts: Optional[List[ContactBase]] = []  # List of Contact objects
    cables: Optional[List[CableBase]]
    team: Optional[str] = None
    riders_checked_in: Optional[List[str]] = []

    class Config:
        orm_mode = True
        from_attributes = True

    # Validator for ObjectId
    @validator('id', pre=True)
    def validate_id(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value


    def save(self):
        """
        Save the ParkBase instance to MongoDB.
        """
        try:
            # Convert the Pydantic model to a dictionary
            park_data = self.dict()

            # Check if the park exists in the database and update, or insert a new one
            existing_park = Park.objects(id=self.id).first()

            if existing_park:
                # Update the existing park document in the database
                existing_park.update(**park_data)
            else:
                # Insert a new park document if it doesn't exist
                new_park = Park(**park_data)
                new_park.save()

            print(f"Park {self.id} saved to database successfully")
        except Exception as e:
            print(f"Failed to save park {self.id}: {e}")
            raise e


