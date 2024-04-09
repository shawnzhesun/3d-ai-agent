from abc import ABC, abstractmethod
from typing import Optional, Type
from sqlalchemy.orm import Session
from textwrap import dedent
from O365 import Account
from ..db import crud
from ..db.models import Message
from ..llm.openai_client import respond_to_messages
from ..tools.tool import BaseTool
from ..tools.microsoft.ms_graph_tool import MicrosoftGraphCalendarTool, MicrosoftGraphEmailTool

class Agent(ABC):
    """
    Base class for all agents.

    Basic flow for agent's thought process:

    1. Upon receiving a message, the agent will first check the message history between itself and the sender.
    2. Determine if the agent can respond the final response, or require extra information by using the tools available to the agent.
    3. If the agent needs to use a tool, the corresponding tool will be called to process the message.
    4. With the processed result of the tool, repeat step 2-4 until the final response can be generated and sent back.
    """
    def __init__(self, db_session: Optional[Session]=None):
        self.db_session = db_session
        self.tool_call_limit = 3

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @property
    def responsibility(self):
        return self._responsibility

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

        tool_call_count = 0
        while tool_call_count < self.tool_call_limit:
            for tool_call in response.tool_calls:
                tool = self.get_tool_from_response(tool_call)
                function_args = tool.parse_function_args(tool_call)
                tool_exec_result = tool.run(**function_args)
                tool_call_message = {
                    "role": "tool",
                    "name": tool.name,
                    "tool_call_id": tool_call.id,
                    "content": tool_exec_result,
                }
                messages.append(tool_call_message)

            tool_call_count += 1
            response = respond_to_messages(messages, tools=self.tools)
            if response.content is not None:
                return response.content

        return "I'm sorry, I'm not able to provide an answer at this time. Could you please clarify your question?"

    def get_tool_from_response(self, tool_call) -> Type[BaseTool]:
        tool_name = tool_call.function.name
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

    def __init__(self, db_session: Optional[Session]=None):
        super().__init__(db_session=db_session)
        self.tools = [
            MicrosoftGraphCalendarTool(),
            MicrosoftGraphEmailTool(),
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