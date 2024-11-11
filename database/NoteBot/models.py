import uuid

from bson import ObjectId
from mongoengine import Document, DateTimeField, StringField, ListField, ReferenceField, DictField, IntField, \
    FloatField, BooleanField, EmailField, EmbeddedDocumentField, EmbeddedDocument
from passlib.context import CryptContext
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime, timezone
from fastapi import UploadFile

# Simplified UtteranceModel without word-level details
class UtteranceModel(BaseModel):
    speaker: str
    start: int
    end: int
    text: str
    confidence: float


# Updated TranscriptionResponseModel focusing on utterances only
class TranscriptionResponseModel(BaseModel):
    utterances: List[UtteranceModel]  # Updated to match AssemblyAI's response format

class TokenUsage(Document):
    transcription_cost = FloatField(required=True)  # Cost of transcription (Whisper)
    input_cost = FloatField(required=True)  # Cost of input (prompt) tokens
    output_cost = FloatField(required=True)  # Cost of output (completion) tokens
    total_cost = FloatField(required=True)  # Total cost (transcription + tokens)

    meta = {'db_alias': 'notebot'}

    def to_dict(self):
        """
        Convert the TokenUsage document to a dictionary for API response.
        """
        data = self.to_mongo().to_dict()

        # Convert ObjectId to string
        if "_id" in data:
            data["id"] = str(data.pop("_id"))

        return data


# Pydantic Model for TokenUsage to store costs
class TokenUsageModel(BaseModel):
    transcription_cost: float  # Cost of transcription (Whisper)
    input_cost: float  # Cost of input (prompt) tokens
    output_cost: float  # Cost of output (completion) tokens
    total_cost: float  # Total cost (transcription + tokens)

    def save(self):
        """ Save TokenUsageModel to MongoDB as a TokenUsage document """
        token_usage = TokenUsage(
            transcription_cost=self.transcription_cost,
            input_cost=self.input_cost,
            output_cost=self.output_cost,
            total_cost=self.total_cost
        )
        token_usage.save()
        return token_usage


class Participant(EmbeddedDocument):
    id = StringField(default=lambda: str(uuid.uuid4()))  # Generates UUID-compatible string if not provided
    name = StringField(required=True)
    role = StringField()
    isHost = BooleanField(required=True)
    additionalNotes = StringField()

    def to_dict(self):
        """
        Convert the Participant document to a dictionary for API response.
        """
        data = self.to_mongo().to_dict()

        # Convert id to a UUID-compatible string if it's an ObjectId
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())
        elif ObjectId.is_valid(data["id"]):
            # Convert ObjectId to UUID-like format
            data["id"] = str(uuid.UUID(bytes=data["id"].binary[:16]))

        return data

# Pydantic model for Participant
class ParticipantModel(BaseModel):
    id: Optional[str] = None  # ID will be automatically handled
    name: str
    role: str  # Updated from position
    isHost: bool
    additionalNotes: Optional[str] = None  # New field to match frontend

# Updated CallDetails Document in MongoDB with embedded participants
class CallDetails(Document):
    date = DateTimeField(required=True)
    callType = StringField()
    notes = StringField()
    participants = ListField(EmbeddedDocumentField('Participant'))  # Store participants directly within CallDetails
    notetype = ListField(StringField())  # Field to store note types
    minutes_elapsed = FloatField()  # Matches `minutesElapsed` in the Swift struct
    title = StringField()  # Optional field
    transcription = DictField()  # Optional field
    note_type_responses = DictField()  # New field to store responses for note types
    token_usage = ReferenceField('TokenUsage')  # Optional field for token usage

    meta = {'db_alias': 'notebot'}

    def to_dict(self):
        """
        Convert the MongoEngine document to a dictionary suitable for JSON serialization.
        Handles nested documents and cleans up MongoDB-specific fields like ObjectId.
        """
        data = self.to_mongo().to_dict()

        # Convert ObjectId to string
        if "_id" in data:
            data["id"] = str(data.pop("_id"))

        # Convert date to Unix timestamp (float)
        if "date" in data and isinstance(data["date"], datetime):
            data["date"] = data["date"].timestamp()  # Convert to Unix timestamp (float)

        # Convert token_usage reference if it exists
        if self.token_usage:
            data["token_usage"] = self.token_usage.to_dict()

        # Convert participants references
        data["participants"] = [participant.to_dict() for participant in self.participants]

        return data

# Updated Pydantic Model for CallDetails
class CallDetailsModel(BaseModel):
    date: datetime
    callType: Optional[str] = None
    notes: str
    participants: List['ParticipantModel']  # Directly included as a list of ParticipantModel
    notetype: List[str]
    minutes_elapsed: float
    title: Optional[str] = None
    transcription: Optional['TranscriptionResponseModel'] = None  # Updated to new transcription model
    note_type_responses: Optional[Dict[str, str]] = None  # Field to store note type responses
    audioFileURL: Optional[str] = None  # Matches frontend audio file URL
    token_usage: Optional['TokenUsageModel'] = None

    # Validator to ensure the date is in UTC
    @validator('date', pre=True)
    def ensure_utc(cls, value):
        # Convert the date to a timezone-aware datetime in UTC if it's not already
        if isinstance(value, str):
            # Parse the string date
            parsed_date = datetime.fromisoformat(value)
            # Check if the parsed date is naive (no timezone) and make it UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC if it has a timezone
                parsed_date = parsed_date.astimezone(timezone.utc)
            return parsed_date
        elif isinstance(value, datetime):
            # If the datetime object is naive, convert it to UTC
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            else:
                # Convert to UTC if it has a timezone
                value = value.astimezone(timezone.utc)
            return value
        return value

    def save(self):
        """
        Save the Pydantic model to MongoEngine database.
        """
        try:
            # Directly include participant data instead of saving separately
            participant_embeds = [Participant(**p.dict()) for p in self.participants]

            token_usage_ref = None
            if self.token_usage:
                token_usage_ref = self.token_usage.save()

            # Convert transcription response to dictionary if it's not None
            transcription_dict = self.transcription.dict() if self.transcription else None

            document = CallDetails(
                date=self.date,
                callType=self.callType,
                notes=self.notes,
                title=self.title,
                minutes_elapsed=self.minutes_elapsed,
                transcription=transcription_dict,  # Save the transcription response
                note_type_responses=self.note_type_responses,
                participants=participant_embeds,  # Directly add embedded participants
                token_usage=token_usage_ref
            )
            document.save()
            print(f"Successfully saved to MongoDB.")
            return document
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# MongoEngine User Document
class NoteBotUser(Document):
    email = EmailField(required=True, unique=True)
    hashed_password = StringField(required=True)
    full_name = StringField(required=True)
    phone_number = StringField(required=True, min_length=10, max_length=15)

    meta = {
        'collection': 'notebotuser',  # Same collection name but separate database
        'db_alias': 'notebot'  # Specifies the NoteBot database
    }


# Pydantic model for registration input validation
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone_number: str = Field(..., min_length=10, max_length=15)


# Pydantic model for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


from enum import Enum

# Define a mapping from note type string to their corresponding descriptions
NOTE_TYPE_DESCRIPTORS = {
    "Action Items": "List any actionable tasks, assignments, or follow-ups identified during the conversation.",
    "Brainstorming Ideas": "Provide a summary of the creative ideas and brainstorming session, highlighting key suggestions.",
    "Client Meeting Recap": "Summarize the key points discussed during the client meeting, including important topics, decisions, or outcomes.",
    "Decision Summary": "Summarize the key decisions made during the meeting and their implications.",
    "Executive Summary": "Provide a high-level overview of the meeting, summarizing the main points and key takeaways.",
    "Feedback Summary": "Summarize the feedback given during the session, highlighting key points and suggestions.",
    "Financial Overview": "Provide a summary of the financial discussion, including key metrics, trends, and financial decisions.",
    "Follow-Up Tasks": "Identify the tasks and follow-ups that were assigned during the meeting.",
    "Key Points": "Highlight the most important points discussed in the conversation.",
    "Meeting Minutes": "Provide detailed meeting minutes, capturing all significant points, decisions, and action items.",
    "Negotiation Outcomes": "Summarize the outcomes of the negotiation, including agreements, compromises, and next steps.",
    "Performance Review Notes": "Summarize key points from the performance review, including feedback and areas for improvement.",
    "Project Planning Notes": "Provide an overview of the project planning session, including timelines, responsibilities, and key objectives.",
    "Risk Assessment": "Summarize the risk assessment discussion, highlighting identified risks and proposed mitigation strategies.",
    "Sales Call Summary": "Summarize the key points from the sales call, including client needs, objections, and next steps.",
    "Strategy Outline": "Provide an outline of the strategy discussed, including main objectives and planned actions.",
    "SWOT Analysis": "Provide an analysis of Strengths, Weaknesses, Opportunities, and Threats discussed during the meeting.",

    # Educational
    "Abstract Summary": "Provide an abstract summary of the main topics discussed.",
    "Action Plan for Improvement": "Outline an action plan for improvement based on the discussion.",
    "Concept Maps": "Summarize the key concepts discussed and their relationships.",
    "Debate Highlights": "Summarize the main arguments and counterarguments from the debate.",
    "Flashcards": "Highlight key terms and concepts that can be turned into flashcards for study purposes.",
    "Important Dates and Deadlines": "List important dates and deadlines discussed.",
    "Key Terms and Definitions": "Summarize the key terms and their definitions as discussed.",
    "Lab Results Summary": "Provide a summary of the lab results and their implications.",
    "Lecture Notes": "Summarize the lecture notes, highlighting the main points and key takeaways.",
    "Parent-Teacher Conference Summary": "Summarize the main points discussed during the parent-teacher conference.",
    "Problem-Solving Steps": "Outline the problem-solving steps discussed during the session.",
    "Q&A Highlights": "Highlight key questions and answers from the session.",
    "Study Guide": "Summarize key topics and concepts that can be used as a study guide.",

    # Personal
    "Budget and Financial Notes": "Summarize the budget and financial notes discussed.",
    "Counseling Insights": "Provide insights from the counseling session.",
    "Creative Ideas List": "Summarize the creative ideas discussed.",
    "Daily Planner": "Summarize key points for daily planning.",
    "Family Meeting Notes": "Summarize the main points discussed during the family meeting.",
    "Goal Tracker": "Summarize the goals discussed and any progress updates.",
    "Gratitude List": "List items discussed for gratitude.",
    "Health and Wellness Log": "Summarize health and wellness points discussed.",
    "Mind Mapping": "Provide a summary of the mind mapping session.",
    "Personal Reflections": "Summarize personal reflections shared during the session.",
    "Score Tracking": "Summarize any score tracking discussed.",
    "Story Outline": "Provide an outline of the story discussed.",
    "Vacation Itinerary": "Summarize the vacation itinerary discussed.",

    # General
    "Agenda Outline": "Provide an outline of the agenda.",
    "Detailed Analysis": "Provide a detailed analysis of the discussion.",
    "FAQs": "Summarize frequently asked questions discussed.",
    "Lessons Learned": "Summarize the lessons learned from the discussion.",
    "Motivational Points": "Summarize the motivational points discussed.",
    "Next Steps": "Identify the next steps to be taken.",
    "Priorities List": "Summarize the priorities discussed.",
    "Pros and Cons List": "List the pros and cons discussed.",
    "Resource List": "Provide a list of resources mentioned.",
    "Summary for Different Audiences": "Provide a summary tailored for different audiences."
}
