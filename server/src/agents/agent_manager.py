from typing import List
from textwrap import dedent
from .agent import Agent
from ..llm.openai_client import respond_to_prompt

class AgentManager:

  @staticmethod
  def analyze_message_for_agent(message_text: str, agents: List[Agent]) -> Agent:
    """
    Determines if a specific role should respond to a message.
    """
    agent_roles = [agent.role for agent in agents]
    agent_values = [{"name": agent.name, "role": agent.role, "responsibility": agent.responsibility} for agent in agents]
    prompt = dedent(f"""
    Who should respond to this message from the company's CEO: {message_text}
    Options: {agent_values}
    Only one role should respond. Please reply with the name of the role only. For example, "CEO Assistant".
    """)
    response = respond_to_prompt(prompt=prompt)
    if response in agent_roles:
      return list(filter(lambda x: x.role == response, agents))[0]
    else:
      raise ValueError(f"Invalid role: {response}")