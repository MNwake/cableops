import mongoengine as db
import dns.resolver
import certifi
from bson import ObjectId


class DataBase:
    host_name = 'cluster0.giawkwl.mongodb.net'
    username = 'admin'
    password = '0C4vS9ougL6uynVy'

    def __init__(self):
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ['1.1.1.1']

        try:
            # Connect to the 'main' database (for shared data like common users)
            db.connect(
                db='main',  # Main database name
                alias='default',  # Alias for the main database connection
                host=f'mongodb+srv://{self.username}:{self.password}@{self.host_name}/main',
                tlsCAFile=certifi.where()
            )
            print("Connected to main MongoDB database.")

            # Connect to the 'Cable' database (for Cable-specific data)
            db.connect(
                db='Cable',  # Cable database name
                alias='cable',  # Alias for the Cable database connection
                host=f'mongodb+srv://{self.username}:{self.password}@{self.host_name}/Cable',
                tlsCAFile=certifi.where()
            )
            print("Connected to Cable MongoDB database.")

            # Connect to the 'notebot' database (for NoteBot-specific data)
            db.connect(
                db='NoteBot',  # notebot database name
                alias='notebot',  # Alias for the notebot database connection
                host=f'mongodb+srv://{self.username}:{self.password}@{self.host_name}/NoteBot',
                tlsCAFile=certifi.where()
            )
            print("Connected to NoteBot MongoDB database.")

        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

        self.cleanup()

    def cleanup(self):
        # self.create_transcript_docx('6712d700af081022c2aaef17')
        pass
    # def create_transcript_docx(self, call_id):
    #     call_detail = self.get_call_details_by_id(call_id)
    #
    #     if call_detail and 'transcription' in call_detail:
    #         transcription = call_detail.transcription
    #         # Save transcription to Word document
    #         self.save_transcription_to_docx(transcription, filename=f"transcription_{call_id}.docx")
    #     else:
    #         print("No transcription data found.")
    #
    # # Function to save transcription to a Word file with speaker "A" text bolded
    # def save_transcription_to_docx(self, transcription, filename='transcription.docx'):
    #     from docx import Document
    #     doc = Document()
    #     doc.add_heading('Transcription', level=1)
    #
    #     # Iterate over the utterances and format text accordingly
    #     for utterance in transcription['utterances']:
    #         speaker = utterance['speaker']
    #         text = utterance['text']
    #
    #         if speaker == 'A':
    #             p = doc.add_paragraph()
    #             p.add_run(text).bold = True  # Speaker "A" text in bold
    #         else:
    #             p = doc.add_paragraph()
    #             p.add_run(text).bold = False
    #
    #     # Save the document as .docx
    #     doc.save(filename)
    #     print(f"Transcription saved to {filename}")
    #
    # # Retrieve the CallDetails by ID
    # def get_call_details_by_id(self, call_id):
    #     from sympy.physics.units import me
    #     try:
    #         # Query MongoDB for the document with the given ObjectId
    #         from NoteBot.models import CallDetails
    #         call_detail = CallDetails.objects.get(id=ObjectId(call_id))
    #         return call_detail
    #     except me.DoesNotExist:
    #         print(f"No call details found for ID: {call_id}")
    #         return None

