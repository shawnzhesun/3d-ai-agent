from openai import AzureOpenAI
from typing import Type
from ..tools.tool import BaseTool
import os

OPENAI_AUTH = str(os.environ["AZURE_OPENAI_KEY"])
client = AzureOpenAI(
    api_key=OPENAI_AUTH,
    api_version="2023-07-01-preview",
    azure_endpoint="https://genai-engx.openai.azure.com",
)

def respond_to_prompt(prompt: str):
    llm_completion = client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
    )
    llm_response = llm_completion.choices[0].message.content
    print(f"LLM Prompt: {prompt}\nLLM Completion: {llm_response}")
    return llm_response

def respond_to_messages(messages, tools: list[Type[BaseTool]]=None):
    if tools is not None:
        tools = [tool.openai_schema for tool in tools]

    llm_completion = client.chat.completions.create(
        model="gpt-35-turbo-16k",
        messages=messages,
        tools=tools,
        temperature=0,
    )
    llm_response = llm_completion.choices[0].message
    print(f"LLM Messages: {messages}\nLLM Completion: {llm_response}")
    messages.append(llm_response)
    return llm_response
