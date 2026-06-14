from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the web for information on the given query."""
    return f"Search results for '{query}': [Top findings: {query} is widely studied...]"

@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    try:
        return str(eval(expression)) 
    except Exception as e:
        return f"Error: {e}"   

@tool
def read_file(path: str) -> str:
    """Read a file from the given path. returns only first 2000 chars"""
    try:
        with open(path, "r") as f:
            return f.read()[:2000]
    except Exception as e:
        return f"Error reading file: {e}"   

TOOLS = [search_web, calculate, read_file]
    