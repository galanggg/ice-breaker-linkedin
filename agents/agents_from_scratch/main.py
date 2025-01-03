import os
from typing import List, Tuple, Union

from text_length import get_text_length
from langchain_core.prompts import PromptTemplate
from langchain_core.tools.render import render_text_description
from langchain_openai import AzureChatOpenAI
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain_core.agents import AgentAction, AgentFinish
from langchain.tools import Tool

api_key = os.environ.get("AZURE_OPENAI_API_KEY")
endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
# print(get_text_length.invoke(input={"text": "Hello World"}))


def find_tool_by_name(tools: list[Tool], tool_name: str) -> Tool:
    for tool in tools:
        if tool.name == tool_name:
            return tool
    raise ValueError(f"Tool with name {tool_name} not found in tools list")


def format_log_to_str(
    intermediate_steps: List[Tuple[AgentAction, str]],
    observation_prefix: str = "Observation: ",
    llm_prefix: str = "Thought: ",
) -> str:
    """Construct the scratchpad that lets the agent continue its thought process ."""
    thoughts = ""
    for action, observation in intermediate_steps:
        thoughts += action.log
        thoughts += f"\n{observation_prefix}{observation}\n{llm_prefix}"
    return thoughts


tools = [get_text_length]
template = """
    Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template=template).partial(
    tools=render_text_description(tools=tools),
    tool_names=", ".join([tool.name for tool in tools]),
)

llm = AzureChatOpenAI(
    model="chronicle-openai-4o",
    api_version="2024-10-01-preview",
    azure_endpoint=endpoint,
    api_key=api_key,
    temperature=0,
    stop_sequences=["\nObservation"],
)
intermediate_steps = []
agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["agent_scratchpad"]),
    }
    | prompt
    | llm
    | ReActSingleInputOutputParser()
)

agent_step = ""
while not isinstance(agent_step, AgentFinish):
    agent_step: Union[AgentAction, AgentFinish] = agent.invoke(
        {
            "input": "What is the length of the text: DOG ?",
            "agent_scratchpad": intermediate_steps,
        }
    )

    print(agent_step)

    if isinstance(agent_step, AgentAction):
        tool_name = agent_step.tool
        tool_to_use = find_tool_by_name(tools, tool_name)
        tool_input = agent_step.tool_input

        observation = tool_to_use.func(str(tool_input))
        print(f"{observation=}")
        intermediate_steps.append((agent_step, str(observation)))

if isinstance(agent_step, AgentFinish):
    print(agent_step.return_values)
