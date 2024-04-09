from datetime import datetime
from O365 import Account
from textwrap import dedent
import os
from ..tool import BaseTool

class MicrosoftGraphCalendarTool(BaseTool):
    name = "microsoft_graph_calendar"

    def __init__(self):
        super().__init__(self.name)
        # Microsoft Authentication Initialization
        credentials = (os.environ["MS_CLIENT_ID"], os.environ["MS_CLIENT_SECRET"])
        account = Account(credentials)
        if account.is_authenticated is False:
            account.authenticate(scopes=['basic', 'mailbox', 'calendar'])
        self.msAccount = account

    @property
    def openai_schema(self):
        today = datetime.now().strftime("%Y-%m-%d")
        tool_schema = {
            "type": "function",
            "function": {
                "name": f"{self.name}",
                "description": f"Get the calendar events from the start time to the end time. Today is {today}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "The start time of the time duration to get the calendar events for, represented in ISO 8601 format.",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "The end time of the time duration to get the calendar events for, represented in ISO 8601 format.",
                        }
                    },
                    "required": ["start_time", "end_time"],
                },
            },
        }
        return tool_schema

    def run(self, start_time: str, end_time: str):
        calendar = self.msAccount.schedule().get_default_calendar()
        q = calendar.new_query('start').greater_equal(start_time)
        q.chain('and').on_attribute('end').less_equal(end_time)
        calendar_events = calendar.get_events(query=q, include_recurring=True)
        all_events = []
        for event in calendar_events:
            all_events.append({
                "subject": event.subject,
                "start": event.start.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": event.end.strftime("%Y-%m-%dT%H:%M:%S"),
                "location": event.location,
            })
        return dedent(f"""
            Calendar Events from {start_time} to {end_time}:
            {all_events}
        """)

class MicrosoftGraphEmailTool(BaseTool):
    name = "microsoft_graph_email"

    def __init__(self):
        super().__init__(self.name)
        # Microsoft Authentication Initialization
        credentials = (os.environ["MS_CLIENT_ID"], os.environ["MS_CLIENT_SECRET"])
        account = Account(credentials)
        if account.is_authenticated is False:
            account.authenticate(scopes=['basic', 'mailbox', 'calendar'])
        self.msAccount = account

    @property
    def openai_schema(self):
        tool_schema = {
            "type": "function",
            "function": {
                "name": f"{self.name}",
                "description": f"Get the emails from the email inbox.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "The keyword to search for in the email subject.",
                        }
                    },
                    "required": ["keyword"],
                },
            },
        }
        return tool_schema

    def run(self, keyword: str):
        mailbox = self.msAccount.mailbox()
        inbox = mailbox.inbox_folder()
        messages = []
        q = inbox.new_query('subject').contains(keyword)
        for message in inbox.get_messages(query=q):
            messages.append({
                "subject": message.subject,
                "from": message.sender.address,
                "is_read": message.is_read,
            })
        return dedent(f"""
            Emails in the inbox:
            {messages}
        """)

