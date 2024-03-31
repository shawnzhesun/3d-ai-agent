from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class MeetingRoom(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    messages: list["Message"] = Relationship(back_populates="meeting_room")

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_name: str
    text: str
    role: str
    timestamp: datetime = Field(default=None)
    meeting_room_id: int = Field(default=None, foreign_key="meetingroom.id")
    meeting_room: MeetingRoom = Relationship(back_populates="messages")
