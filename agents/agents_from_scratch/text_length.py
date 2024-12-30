from langchain.agents import tool


@tool
def get_text_length(text: str) -> int:
    """Get the length of a text."""
    print(f"get_text_length enter with: {text=}")
    text = text.strip("'\n").strip('"')
    return len(text)
