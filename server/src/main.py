from .audio import audio
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, SQLModel, create_engine
from .db import crud
from .agents.agent import AssistantAgent, EngineeringManagerAgent



app = FastAPI()

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///./{sqlite_file_name}"

engine = create_engine(
    sqlite_url, echo=True, connect_args={"check_same_thread": False}
)

agents = []

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        # Check for the default meeting room
        default_meeting_room = crud.get_meeting_room_by_id(db, id=1)
        if not default_meeting_room:
            # Create the default meeting room if it doesn't exist
            crud.create_meeting_room(db, id=1)

        assistant_agent = AssistantAgent(db_session=db)
        engineering_manager_agent = EngineeringManagerAgent(db_session=db)
        agents.append(assistant_agent)
        agents.append(engineering_manager_agent)

        assistant_agent.post_message("Hello, I'm here to assist the CEO.")
        engineering_manager_agent.post_message("Hello, I'm the Engineering Manager.")


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
def messages(meeting_room_id: int):
    with Session(engine) as db:
        db_messages = crud.messages(db, meeting_room_id)
        if db_messages is None:
            raise HTTPException(status_code=404, detail=f"Messages not found for meeting room {meeting_room_id}")
        return db_messages

@app.post("/messages")
def create_message(user_name: str, text: str, role: str, meeting_room_id: int=1):
    with Session(engine) as db:
        db_message = crud.create_message(db, user_name=user_name, text=text, role=role, meeting_room_id=meeting_room_id)
        return db_message


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
