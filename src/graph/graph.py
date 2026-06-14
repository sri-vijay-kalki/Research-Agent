from langgraph.types import interrupt
from langgraph.graph import StateGraph,END,START
from langgraph.prebuilt import ToolNode
from src.state.state import ResearchState
from src.config.llm_client import LLMClient
from src.tools.tools import TOOLS
from src.schemas.schemas import ResearchPlan,Evaluation
from src.utils.formatter import print_report_styled, print_feedback_styled

#define nodes

def planner_node(state:ResearchState):
    print("planning phase started with topic",state["topic"])   
    planner = LLMClient.get_client().with_structured_output(ResearchPlan)
    plan = planner.invoke(f"""Break this research topic into 3 focused sub-questions: {state['topic']}""")
    subtopic_dict = {}
    for subtopic in plan.sub_questions:
        subtopic_dict[subtopic] = []    
    print("planning phase completed with fetching subtopics of length ",len(subtopic_dict))
    return {"research_data": subtopic_dict}

def researcher_node(state:ResearchState):
    print("research phase started")
    client = LLMClient.get_client().bind_tools(tools=TOOLS)
    new_data = {}

    # Build a feedback hint if this is a re-research loop
    feedback_hint = ""
    if state.get("feedback"):
        feedback_hint = f"\nThe previous report was scored {state.get('score', '?')}/10. Feedback: {state['feedback']}\nFocus your research on addressing these gaps."

    for sub_topic in state["research_data"]:
        prompt = f"Gather detailed research data for: {sub_topic}{feedback_hint}"
        response = client.invoke(prompt)
        if response.tool_calls:
            print(f"  tool calls for '{sub_topic[:50]}': {[tc['name'] for tc in response.tool_calls]}")
            tool_node = ToolNode(tools=TOOLS)
            tool_output = tool_node.invoke(response.tool_calls)
            new_data[sub_topic] = [response.content, str(tool_output)]
        else:
            new_data[sub_topic] = [response.content]

    print("research phase completed with", len(new_data), "sub-topics")
    return {"research_data": new_data}

def writer_node(state:ResearchState):
    print("writing phase started")
    client = LLMClient.get_client()

    # If we have a previous draft + feedback, ask to improve it
    revision_section = ""
    if state.get("report") and state.get("feedback"):
        revision_section = f"""
        IMPORTANT: This is a revision. Here is the previous draft:
        {state['report']}

        The evaluator gave this feedback:
        {state['feedback']}

        Improve the draft based on this feedback. Do NOT start from scratch.
        """

    prompt = f"""
        You are a professional research writer.
        Write a research report on the topic: {state['topic']}
        Use all findings below: {state['research_data']}
        {revision_section}
    """
    response = client.invoke(prompt)
    print("writing phase completed, report length:", len(response.content))
    return {"report": response.content}

def evaluator_node(state:ResearchState):
    print("evaluation phase started")
    evaluator = LLMClient.get_client(temperature=0.1).with_structured_output(Evaluation)
    prompt = f"""
        You are a HARSH research evaluator. You rarely give scores above 7.

        Scoring guide:
        - 1-3: Missing major sections, factual errors, or off-topic
        - 4-6: Covers the topic but lacks depth, specifics, or citations
        - 7-8: Solid report with minor gaps
        - 9-10: Publication-ready, comprehensive, well-structured

        Most first drafts deserve a 4-6. Be critical.

        Topic: {state['topic']}
        Report: {state['report']}
    """
    response = evaluator.invoke(prompt)
    print(f"evaluation: score={response.score}, attempts={state['attempts'] + 1}")
    print(f"feedback: {response.feedback[:200]}...")

    # Display using beautiful formatting
    print_report_styled(state['report'], title=f"Research Report (Attempt {state['attempts'] + 1})")
    print_feedback_styled(response.feedback, response.score)
    
    return {
        "score": response.score,
        "feedback": response.feedback,
        "attempts": state["attempts"] + 1
    }
    
def route_after_evaluator(state:ResearchState):
    if state["attempts"]>=3 or state["score"]>=8:
        return "approve"
    else:
        return "researcher"

def approve_node(state:ResearchState):
    print("approval phase started")

    desicion = interrupt({
        "report":state["report"],
        "message":"reply 'approve' or 'reject' and provide feedback"
    })
    print("desicion:",desicion)
    
    if desicion.strip().lower() == "approve":
        return {"feedback": "approved"}
    elif desicion.strip().lower() == "reject":
        return {"feedback": "rejected"}
    else:
        return {"feedback":desicion}

def route_after_approval(state:ResearchState):
    if state["feedback"] in ("approved", "rejected"):
        return END   
    else:
        return "researcher"


def get_compiler_graph(checkpointer = ""):
    graph = StateGraph(ResearchState)

    graph.add_node("planner",planner_node)
    graph.add_node("researcher",researcher_node)
    graph.add_node("writer",writer_node)
    graph.add_node("evaluator",evaluator_node)
    graph.add_node("approve",approve_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner","researcher")
    graph.add_edge("researcher","writer")
    graph.add_edge("writer","evaluator")
    graph.add_conditional_edges("evaluator",route_after_evaluator,["researcher","approve"])
    graph.add_conditional_edges("approve",route_after_approval,["researcher",END])

    return graph.compile(checkpointer=checkpointer)
        
if __name__ == "__main__":
    graph = get_compiler_graph()
    state = ResearchState(topic="Machine Learning")
    result = graph.draw_ascii()
    print(result)