from src.config import config
from src.config.llm_client import LLMClient
from src.state.state import ResearchState
from src.graph.graph import get_compiler_graph
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from src.utils.formatter import print_interrupt_payload_styled, print_markdown, save_graph_image


if __name__ == "__main__":
    conf = {"configurable":{"thread_id":"thread_1"}}
    client = LLMClient.get_client()
    graph=get_compiler_graph(MemorySaver())
    
    # Save the graph visualization as a PNG image
    save_graph_image(graph)
    initial_state=ResearchState(topic="Explain the theory of langraph in 300 words. ",attempts=0)
    response=graph.invoke(initial_state,conf)

    interrupts = response.get("__interrupt__",[])
    for interrupt in interrupts:
         print_interrupt_payload_styled(interrupt.value)

    human_input = input("approve / reject/ provide feedback : ")

    final = graph.invoke(Command(resume=human_input),conf)

    print("\n" + "="*40 + " FINAL REPORT " + "="*40)
    print_markdown(final["report"])