import datetime

from bson import ObjectId
import numpy as np

def custom_encoder(obj):
    if isinstance(obj, ObjectId):
        # Convert ObjectId to string
        return str(obj)
    elif isinstance(obj, (list, set)):
        # Recursively apply custom_encoder to each item in the list or set
        return [custom_encoder(item) for item in obj]
    elif isinstance(obj, dict):
        # Recursively apply custom_encoder to each value in the dict
        return {key: custom_encoder(value) for key, value in obj.items()}
    elif isinstance(obj, datetime.datetime):
        # Convert datetime objects to string (or any other format you prefer)
        return obj.isoformat()
    elif isinstance(obj, float) and np.isnan(obj):
        # Replace NaN with None
        return None

    # Add additional conditions here for other data types you might encounter
    return obj
