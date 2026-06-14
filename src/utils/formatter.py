from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

def print_markdown(text: str):
    """Prints raw markdown beautifully in the terminal."""
    console.print(Markdown(text))

def print_report_styled(report: str, title: str = "Research Report Draft"):
    """Prints a research report wrapped in a nice Rich panel with markdown formatting."""
    print("\n" + "="*80)
    console.print(Panel(Markdown(report), title=title, border_style="cyan"))
    print("="*80 + "\n")

def print_feedback_styled(feedback: str, score: int):
    """Prints evaluation feedback styled with Rich."""
    color = "green" if score >= 7 else "yellow" if score >= 4 else "red"
    title = f"Evaluator Feedback (Score: {score}/10)"
    console.print(Panel(feedback, title=title, border_style=color))

def print_interrupt_payload_styled(payload: dict):
    """Prints the interrupt message and report beautifully."""
    if isinstance(payload, dict):
        message = payload.get("message", "User action required")
        report = payload.get("report", "")
        console.print(Panel(message, title="ATTENTION: Human Review Required", border_style="magenta"))
        if report:
            print_report_styled(report, title="Report Draft for Review")
    else:
        console.print(Panel(str(payload), title="Pause Notification", border_style="magenta"))

def save_graph_image(graph, filepath: str = "graph.png"):
    """Saves the compiled graph visualization as a PNG image."""
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        with open(filepath, "wb") as f:
            f.write(png_bytes)
        print(f"Graph visualization saved successfully as '{filepath}'!")
    except Exception as e:
        print(f"Could not save graph image to '{filepath}': {e}")
