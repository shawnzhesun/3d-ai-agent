from sqlalchemy.orm import Session
from datetime import datetime
from . import models


def meeting_rooms(db: Session):
    return db.query(models.MeetingRoom).all()

def get_meeting_room_by_id(db: Session, id: int):
    return db.query(models.MeetingRoom).filter(models.MeetingRoom.id==id).first()

def create_meeting_room(db: Session, id: int):
    db_room = models.MeetingRoom(id=id, messages=[])
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def create_message(db: Session, user_name: str, text: str, role: str, meeting_room_id: int):
    db_message = models.Message(user_name=user_name, text=text, role=role, timestamp=datetime.now(), meeting_room_id=meeting_room_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def messages(db: Session, meeting_room_id: int):
    return db.query(models.Message).filter(models.Message.meeting_room_id==meeting_room_id).order_by(models.Message.timestamp).all()
