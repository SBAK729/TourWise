from langgraph.graph import StateGraph, START, END
from app.agents.state import AssistantState
from app.agents.guide_agent import node_guide_agent
from app.agents.budget_agent import node_budget_agent
from app.agents.language_agent import node_language_agent
from app.agents.coordinator_agent import node_coordinator_agent


def build_travel_graph():
    """Build and compile the travel workflow graph."""
    workflow = StateGraph(AssistantState)

    # Register all agents as nodes
    workflow.add_node("GuideAgent", node_guide_agent)
    workflow.add_node("BudgetAgent", node_budget_agent)
    workflow.add_node("LanguageAgent", node_language_agent)
    workflow.add_node("CoordinatorAgent", node_coordinator_agent)

    # Define workflow order
    workflow.add_edge(START, "GuideAgent")
    workflow.add_edge("GuideAgent", "BudgetAgent")
    workflow.add_edge("BudgetAgent", "LanguageAgent")
    workflow.add_edge("LanguageAgent", "CoordinatorAgent")
    workflow.add_edge("CoordinatorAgent", END)


    return workflow.compile()


def run_travel_graph(state: AssistantState):
    """Execute the compiled travel graph using the provided state."""
    graph = build_travel_graph()

    result = graph.invoke(state)

    if hasattr(result, "dict"):
        result = result.dict()
    elif hasattr(result, "__dict__"):
        result = vars(result)

    return result
