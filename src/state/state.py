from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

def merge_research(old_data:dict[str,list[str]], new_data: dict[str,list[str]]) -> dict[str,list[str]]:
    merged=old_data.copy()
    for key, value in new_data.items():
        if key not in merged:
            merged[key]=list(value)
        else:
            merged[key].extend(value)
    return merged    

class ResearchState(TypedDict):
    topic : str
    research_data : Annotated[dict[str,list[str]],merge_research]
    report: str
    score : int
    attempts : int
    feedback : str
    messages: Annotated[list[AnyMessage],add_messages]


    
    