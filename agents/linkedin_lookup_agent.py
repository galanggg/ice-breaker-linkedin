import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from tools.tools import get_profile_url_tavily
from langchain_openai import AzureChatOpenAI


def lookup(name: str):
    # llm = ChatOpenAI(base_url="http://localhost:1234/v1")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    llm = AzureChatOpenAI(
        model="chronicle-openai-4o",
        api_version="2024-10-01-preview",
        azure_endpoint=endpoint,
        api_key=api_key,
        temperature=0.8,
    )

    template = """given the full name {name} I want you to get it me a link to their Linkedin profile page. Your answer should contain only a URL"""
    prompt_template = PromptTemplate(input_variables=["name"], template=template)
    tools_for_agent = [
        Tool(
            name="Crawl Google 4 LinkedIn profile page",
            func=get_profile_url_tavily,
            description="useful for when you need get the Linkedin Page URL",
        )
    ]

    react_prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm, tools=tools_for_agent, prompt=react_prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools_for_agent,
        verbose=True,
        handle_parsing_errors=True,
    )

    result = agent_executor.invoke(
        input={"input": prompt_template.format_prompt(name=name)},
    )
    print("Result in Agent: ", result)
    linkedin_url = result["output"]
    return linkedin_url
