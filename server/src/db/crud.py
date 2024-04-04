from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from typing import List
from ..agents.agent import Agent
from ..agents.agent_manager import AgentManager
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

def create_message(db: Session, user_name: str, text: str, role: str, to_role: str, meeting_room_id: int):
    db_message = models.Message(user_name=user_name, text=text, role=role, timestamp=datetime.now(), to_role=to_role, meeting_room_id=meeting_room_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message_to_role(db: Session, message_id: int, to_role: str):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    db_message.to_role = to_role
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def messages(db: Session, meeting_room_id: int):
    return db.query(models.Message).filter(models.Message.meeting_room_id==meeting_room_id).order_by(models.Message.timestamp).all()

def messages_between_roles(db: Session, role1: str, role2: str):
    return db.query(models.Message)\
             .filter(or_(and_(models.Message.role==role1, models.Message.to_role==role2), and_(models.Message.role==role2, models.Message.to_role==role1)))\
             .order_by(models.Message.timestamp).all()

def process_message(db: Session, message_id: int, agents: List[Agent]):
    message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not message:
        return

    # Do not reply unless the message is from the CEO to avoid agents talking to each other in a loop
    if message.role != "CEO":
        return

    responding_agent = AgentManager.analyze_message_for_agent(message.text, agents)

    if responding_agent is not None:
        update_message_to_role(db, message_id, responding_agent.role)
        agent_response = responding_agent.respond(message)
        responding_agent.post_message(agent_response, to_role=message.role, meeting_room_id=message.meeting_room_id)
