from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from ..db import crud

class Agent(ABC):
    def __init__(self, db_session: Optional[Session]=None):
        self.db_session = db_session

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @abstractmethod
    def system_message(self):
        pass

    def post_message(self, text: str, meeting_room_id: int=1):
        if not self.db_session:
            raise ValueError("Database session is not available for this agent.")

        message = crud.create_message(self.db_session,
                                      user_name=self.name,
                                      text=text,
                                      role=self.role,
                                      meeting_room_id=meeting_room_id)
        return message


class AssistantAgent(Agent):
    _name = "Amy"
    _role = "CEO Assistant"

    def system_message(self):
        return f"""
You are the Chief Executive Officer's assistent {self.name}. You work at C3.ai and your main responsibility as a CEO's assistant is to provide administrative support to the CEO and coordinate the CEO's questions.
You are a key member of the CEO's team and play a crucial role in ensuring the CEO's questions get answered by the right person, and you need to be able to communicate effectively with the CEO with the information provided by other members in the company.
        """


class EngineeringManagerAgent(Agent):
    _name = "Michael"
    _role = "Engineering Manager"

    def system_message(self):
        return f"""
You are the Software Engineering Manager {self.name}. You work at C3.ai and your main responsibility as an Engineering Manager is to provide update on software development progress.
Your team is using Jira to manage the software development process. You need to be able to communicate effectively with the CEO and other team members to ensure the software development process is on track.
        """