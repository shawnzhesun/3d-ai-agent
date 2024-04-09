import asyncio
import configparser
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from sqlmodel import Session, SQLModel, create_engine
from O365 import Account
import readline

# Config Initialization
config = configparser.ConfigParser()
config.read(["../config.cfg"])
os.environ["OPENAI_API_KEY"] = config["openai"]["apiKey"]
os.environ["AZURE_OPENAI_KEY"] = config["azure-openai"]["apiKey"]
os.environ["MS_CLIENT_ID"] = config["azure"]["clientId"]
os.environ["MS_CLIENT_SECRET"] = config["azure"]["clientSecret"]

# from .audio import audio
from .db import crud
from .agents.agent import AssistantAgent, EngineeringManagerAgent
from .llm.openai_client import respond_to_prompt


# FastAPI Initialization
app = FastAPI()

# Database Initialization
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///./{sqlite_file_name}"
engine = create_engine(
    sqlite_url, echo=False, connect_args={"check_same_thread": False}
)

# Agent Initialization
agents = []

ceo_name = config["app"]["ceoName"]
ceo_email = config["app"]["ceoEmail"]


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        default_meeting_room = crud.get_meeting_room_by_id(db, id=1)
        if not default_meeting_room:
            crud.create_meeting_room(db, id=1)

        assistant_agent = AssistantAgent(db_session=db)
        engineering_manager_agent = EngineeringManagerAgent(db_session=db)
        agents.append(assistant_agent)
        agents.append(engineering_manager_agent)


@app.get("/meeting_rooms")
def meeting_rooms():
    with Session(engine) as db:
        db_room = crud.meeting_rooms(db)
        if db_room is None:
            raise HTTPException(status_code=404, detail="Meeting room not found")
        return db_room

@app.post("/meeting_rooms")
def create_meeting_room(id: int):
    with Session(engine) as db:
        db_room = crud.create_meeting_room(db, id=id)
        return db_room

@app.get("/messages")
def messages(meeting_room_id: int=1):
    with Session(engine) as db:
        db_messages = crud.messages(db, meeting_room_id)
        if db_messages is None:
            raise HTTPException(status_code=404, detail=f"Messages not found for meeting room {meeting_room_id}")
        return db_messages

@app.post("/messages")
def create_message(user_name: str, text: str, role: str, background_tasks: BackgroundTasks, to_role: str=None, meeting_room_id: int=1):
    with Session(engine) as db:
        db_message = crud.create_message(db, user_name=user_name, text=text, role=role, to_role=to_role, meeting_room_id=meeting_room_id)
        background_tasks.add_task(crud.process_message, db, db_message.id, agents)
        return db_message

@app.get("/new_user_message")
def new_user_message(text: str, background_tasks: BackgroundTasks):
    return create_message(text=text, user_name=ceo_name, role="CEO", background_tasks=background_tasks, meeting_room_id=1)

@app.get("/messages_between_roles")
def messages_between_roles(role1: str, role2: str):
    with Session(engine) as db:
        db_messages = crud.messages_between_roles(db, role1, role2)
        if db_messages is None:
            raise HTTPException(status_code=404, detail=f"Messages not found between roles {role1} and {role2}")
        return db_messages


@app.post("/test_prompt")
def test_prompt(prompt:str=None):
    return respond_to_prompt(prompt=prompt)

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/generate_json_from_mp3")
# def mouth_shapes():
#     return audio.generate_json_from_mp3("/Users/shawnsun/github/3d-ai-agent/react/public/audios/newMessage.mp3")

# @app.get("/speech_to_text")
# def speech_to_text():
#     return audio.speech_to_text("/Users/shawnsun/github/3d-ai-agent/react/public/audios/newMessage.mp3")

# @app.get("/text_to_speech")
# def text_to_speech():
#     return audio.text_to_speech("Hello, how are you?", "/Users/shawnsun/github/3d-ai-agent/react/public/audios/greeting.mp3")
