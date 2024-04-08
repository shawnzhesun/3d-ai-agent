from abc import ABC, abstractmethod
from datetime import datetime
import json

class BaseTool(ABC):
    """
    Base class for all tools.
    """
    def __init__(self, name):
        self.name = name

    @property
    @abstractmethod
    def openai_schema(self):
        pass

    @abstractmethod
    def run(self, **kwargs):
        pass

    def parse_function_args(self, tool_call):
        return json.loads(tool_call.function.arguments)
