from abc import ABC, abstractmethod
from typing import Optional, Type
from sqlalchemy.orm import Session
from textwrap import dedent
from ..db import crud
from ..db.models import Message
from ..llm.openai_client import respond_to_messages
from ..tools.tool import BaseTool, Office365CalendarTool

class Agent(ABC):
    def __init__(self, db_session: Optional[Session]=None):
        self.db_session = db_session

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @property
    def responsibility(self):
        return self._responsibility

    @property
    def tools(self) -> list[Type[BaseTool]]:
        return self._tools

    @abstractmethod
    def system_message(self):
        pass

    def respond(self, message: Message):
        message_history = crud.messages_between_roles(self.db_session, role1=self.role, role2=message.role)
        messages = []
        messages.append({"role": "system", "content": self.system_message()})
        for m in message_history:
            if m.role == self.role:
                messages.append({"role": "assistant", "content": m.text})
            elif m.role == message.role:
                messages.append({"role": "user", "content": m.text})
        response = respond_to_messages(messages, tools=self.tools)
        if response.content is not None:
            return response.content

        tool = self.get_tool_from_response(response)
        function_args = tool.parse_function_args(response)
        tool_exec_result = tool.run(**function_args)
        final_response = tool.process_result(tool_exec_result)
        return final_response

    def get_tool_from_response(self, response) -> Type[BaseTool]:
        tool_name = response.tool_calls[0].function.name
        for t in self.tools:
            if t.name == tool_name:
                return t
        raise ValueError(f"Tool {tool_name} not found in tools list.")

    def post_message(self, text: str, to_role:str=None, meeting_room_id: int=1):
        if not self.db_session:
            raise ValueError("Database session is not available for this agent.")

        message = crud.create_message(self.db_session,
                                      user_name=self.name,
                                      text=text,
                                      role=self.role,
                                      to_role=to_role,
                                      meeting_room_id=meeting_room_id)
        return message


"""
### Assistant ###
"""
class AssistantAgent(Agent):
    _name = "Amy"
    _role = "CEO Assistant"
    _responsibility = "provide administrative support to the CEO and coordinate the CEO's schedule"
    _tools = [
        Office365CalendarTool(),
    ]

    def system_message(self):
        return dedent(f"""
            You are the Chief Executive Officer's assistent {self.name}. You work at C3.ai and your main responsibility as a CEO's assistant is to {self.responsibility}.
            You are a key member of the CEO's team and play a crucial role in ensuring the CEO's questions get answered by the right person, and you need to be able to communicate effectively with the CEO with the information provided by other members in the company.
        """)


"""
### Engineering ###
"""
class EngineeringManagerAgent(Agent):
    _name = "Michael"
    _role = "Engineering Manager"
    _responsibility = "provide update on software development and release progress"

    def system_message(self):
        return dedent(f"""
            You are the Software Engineering Manager {self.name}. You work at C3.ai and your main responsibility as an Engineering Manager is to {self.responsibility}.
            Your team is using Jira to manage the software development process. You need to be able to communicate effectively with the CEO and other team members to ensure the software development process is on track.
        """)