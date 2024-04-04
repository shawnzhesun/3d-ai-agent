from abc import ABC, abstractmethod
from datetime import datetime
import json

class BaseTool(ABC):
    def __init__(self, name):
        self.name = name

    @property
    @abstractmethod
    def openai_schema(self):
        pass

    @abstractmethod
    def run(self, **kwargs):
        pass

    @abstractmethod
    def process_result(self, result):
        pass

    def parse_function_args(self, response):
        return json.loads(response.tool_calls[0].function.arguments)


class Office365CalendarTool(BaseTool):
    name = "office_365_calendar"

    def __init__(self):
        super().__init__(self.name)

    @property
    def openai_schema(self):
        today = datetime.now().strftime("%Y-%m-%d")
        tool_schema = {
            "type": "function",
            "function": {
                "name": f"{self.name}",
                "description": f"Get the schedule for CEO for this week. Today is {today}.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "The start time of this work week (Monday morning 9am)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "The end time of this work week (Friday afternoon 5pm)",
                        }
                    },
                    "required": ["start_time", "end_time"],
                },
            },
        }
        return tool_schema

    def run(self, **kwargs):
        print(f"Executing Office365Tool with {kwargs}")
        return "Office365Tool executed successfully"

    def process_result(self, result):
        print(f"Processing result: {result}")
        return "Office365Tool processed successfully"