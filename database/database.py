import os
import mongoengine as db
import dns.resolver
import certifi
from bson import ObjectId
from dotenv import load_dotenv



class DataBase:
    def __init__(self):
        # Load environment variables from a .env file (optional)
        load_dotenv()

        # Retrieve credentials from environment variables
        self.host_name = os.getenv('MONGO_HOST', 'cluster0.giawkwl.mongodb.net')
        self.username = os.getenv('MONGO_USER', 'admin')
        self.password = os.getenv('MONGO_PASS', 'password')

        # Configure DNS resolver
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ['1.1.1.1']

        # Connect to databases
        try:
            self.connect_to_database('main', alias='default')  # Main database
            self.connect_to_database('Cable', alias='cable')  # Cable database
            self.connect_to_database('NoteBot', alias='notebot')  # NoteBot database
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

        self.cleanup()

    def connect_to_database(self, db_name, alias):
        """Connect to a MongoDB database with the given name and alias."""
        try:
            db.connect(
                db=db_name,
                alias=alias,
                host=f'mongodb+srv://{self.username}:{self.password}@{self.host_name}/{db_name}',
                tlsCAFile=certifi.where()
            )
            print(f"Connected to {db_name} MongoDB database.")
        except Exception as e:
            print(f"Error connecting to {db_name} database: {e}")

    def cleanup(self):
        """Placeholder for any cleanup actions after connecting to the database."""
        pass
