import certifi
import dns
import mongoengine as db



class DataBase:
    host_name = 'cluster0.giawkwl.mongodb.net'
    username = 'admin'
    password = '0C4vS9ougL6uynVy'

    def __init__(self):
        self.archive = None
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ['1.1.1.1']

        try:
            self.database_name = 'main'  # Replace with your database name
            db.connect(
                db=self.database_name,
                alias='default',  # Set to 'default' for default connection
                host=f'mongodb+srv://{self.username}:{self.password}@{self.host_name}/{self.database_name}',
                tlsCAFile=certifi.where()
            )
            print("Connected to MongoDB")
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            
        self.cleanup()

    def cleanup(self):
        pass

# Initialize the database connection
