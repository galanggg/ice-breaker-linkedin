from langchain_community.tools.tavily_search import TavilySearchResults
import os

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


def get_profile_url_tavily(name: str):
    """Searches for Linkedin or Twitter Profile Page."""
    search_results = TavilySearchResults()
    res = search_results.run(f"{name}")
    return res
