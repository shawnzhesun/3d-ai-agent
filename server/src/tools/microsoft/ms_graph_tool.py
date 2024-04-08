from datetime import datetime
from ..tool import BaseTool
from .graph import Graph

class MicrosoftGraphTool(BaseTool):
    name = "microsoft_graph"

    def __init__(self, graph: Graph):
        super().__init__(self.name)
        self.graph = graph

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

    def run(self, start_time, end_time):
        return f"From {start_time} to {end_time} - 9am: Meeting with Engineering Manager\n10am: Meeting with Assistant\n11am: Meeting with Marketing Manager\n12pm: Lunch\n1pm: Meeting with Sales Manager\n2pm: Meeting with HR Manager\n3pm: Meeting with Finance Manager\n4pm: Meeting with CEO Assistant\n5pm: End of day\n"

