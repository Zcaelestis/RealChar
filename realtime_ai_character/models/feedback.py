# Importing necessary modules
import datetime
from sqlalchemy import Column, String, DateTime, Unicode
from sqlalchemy.inspection import inspect
from pydantic import BaseModel
from realtime_ai_character.database.base import Base
from typing import Optional

# Defining a Feedback class that inherits from the Base class
class Feedback(Base):
    # Defining the name of the table in the database
    __tablename__ = "feedbacks"

    # Defining the columns of the table
    message_id = Column(String(64), primary_key=True)
    session_id = Column(String(50), nullable=True)
    user_id = Column(String(50), nullable=True)
    server_message_unicode = Column(Unicode(65535), nullable=True)
    feedback = Column(String(100), nullable=True)
    comment = Column(Unicode(65535), nullable=True)
    created_at = Column(DateTime(), nullable=False)

    # Defining a method to convert the Feedback object to a dictionary
    def to_dict(self):
        return {
            c.key:
            # If the value is a datetime object, convert it to an ISO formatted string
            getattr(self, c.key).isoformat() if isinstance(
                getattr(self, c.key), datetime.datetime) else getattr(
                    self, c.key)
            # Iterate over all the columns of the table
            for c in inspect(self).mapper.column_attrs
        }

    # Defining a method to save the Feedback object to the database
    def save(self, db):
        db.add(self)
        db.commit()

# Defining a FeedbackRequest class that inherits from the BaseModel class
class FeedbackRequest(BaseModel):
    # Defining the attributes of the FeedbackRequest object
    message_id: str
    session_id: Optional[str] = None
    server_message_unicode: Optional[str] = None
    feedback: Optional[str] = None
    comment: Optional[str] = None
