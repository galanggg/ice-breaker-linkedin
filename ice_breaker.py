import os
from typing import Tuple

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from third_parties.linkedin import scrape_linkedin_profile
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent
from output_parsers import summary_parser, Summary
from langchain_community.llms.gpt4all import GPT4All
from langchain_openai import AzureChatOpenAI


def ice_breaker_with(name: str) -> Tuple[Summary, str]:
    # api_key = os.environ.get("GOOGLE_API_KEY")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    linkedin_username = linkedin_lookup_agent(name=name)
    print("LinkedIn Username Variable: ", linkedin_username)
    linkedin_data = scrape_linkedin_profile(
        linkedin_profile_url=linkedin_username, mock=False
    )
    summary_template = """
        given the LinkedIn information {information} about a person I want you to create:
        - A short summary
        - Two interesting facts about the person
        \n{format_instructions}
        """

    summary_prompt_template = PromptTemplate(
        input_variables=["information"],
        template=summary_template,
        partial_variables={
            "format_instructions": summary_parser.get_format_instructions()
        },
    )

    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    # llm = ChatOpenAI(base_url="http://localhost:1234/v1")
    # llm = ChatOllama(model="llama3.2:3b")
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash", api_key=api_key, temperature=0
    # )
    # local_path = "./models/Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"
    # llm = GPT4All(model=local_path)
    llm = AzureChatOpenAI(
        model="chronicle-openai-4o",
        api_version="2024-10-01-preview",
        azure_endpoint=endpoint,
        api_key=api_key,
    )

    # chain = summary_prompt_template | llm | StrOutputParser()
    chain = summary_prompt_template | llm | summary_parser
    res: Summary = chain.invoke(input={"information": linkedin_data})
    return res, linkedin_data.get("profile_pic_url")


if __name__ == "__main__":
    print("Ice Breaker Enter!")
    ice_breaker_with(name="Galang Kerta")
