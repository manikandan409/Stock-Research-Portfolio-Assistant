from typing import TypedDict
import sys
import os

# -----------------------------------------
# Add project root to Python path
# -----------------------------------------

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from langgraph.graph import StateGraph, START, END

from backend.agents.supervisor import supervisor
from backend.agents.fundamental_agent import fundamental_agent
from backend.agents.sentiment_agent import sentiment_agent
from backend.agents.risk_agent import risk_agent
from backend.agents.rag_agent import rag_agent
from backend.agents.report_agent import report_agent


# ==================================================
# RESEARCH STATE
# ==================================================

class ResearchState(TypedDict, total=False):

    symbol: str
    question: str

    portfolio_symbols: list[str]
    portfolio_weights: list[float]

    research_type: str

    fundamental_data: dict
    sentiment_data: dict
    risk_data: dict
    rag_data: dict

    final_report: dict


# ==================================================
# SUPERVISOR NODE
# ==================================================

def run_supervisor(state: ResearchState):

    print("\n[SUPERVISOR] Starting...")

    result = supervisor(state)

    return result


# ==================================================
# FUNDAMENTAL NODE
# ==================================================

def run_fundamental(state: ResearchState):

    print("\n[FUNDAMENTAL AGENT] Running...")

    result = fundamental_agent(
        state["symbol"]
    )

    return {
        "fundamental_data": result
    }


# ==================================================
# SENTIMENT NODE
# ==================================================

def run_sentiment(state: ResearchState):

    print("\n[SENTIMENT AGENT] Running...")

    result = sentiment_agent(
        state["symbol"]
    )

    return {
        "sentiment_data": result
    }


# ==================================================
# RISK NODE
# ==================================================

def run_risk(state: ResearchState):

    print("\n[RISK AGENT] Running...")

    symbols = state.get(
        "portfolio_symbols",
        [state["symbol"]]
    )

    weights = state.get(
        "portfolio_weights",
        [1.0]
    )

    result = risk_agent(
        symbols,
        weights
    )

    return {
        "risk_data": result
    }


# ==================================================
# RAG NODE
# ==================================================

def run_rag(state: ResearchState):

    print("\n[RAG AGENT] Running...")

    result = rag_agent(
        state["question"]
    )

    return {
        "rag_data": result
    }


# ==================================================
# REPORT NODE
# ==================================================

def generate_report(state: ResearchState):

    print("\n[REPORT AGENT] Generating report...")

    report = report_agent(
        state["symbol"],
        state.get(
            "fundamental_data",
            {}
        ),
        state.get(
            "sentiment_data",
            {}
        ),
        state.get(
            "risk_data",
            {}
        )
    )

    return {
        "final_report": report
    }


# ==================================================
# SUPERVISOR ROUTER
# ==================================================

def route_from_supervisor(state: ResearchState):

    research_type = state.get(
        "research_type",
        "full_research"
    )

    print(
        f"\n[ROUTER] Research type: {research_type}"
    )

    # -----------------------------------------
    # Complete research
    # -----------------------------------------

    if research_type == "full_research":

        return [
            "fundamental",
            "sentiment",
            "risk"
        ]

    # -----------------------------------------
    # Fundamental research
    # -----------------------------------------

    if research_type == "fundamental":

        return [
            "fundamental"
        ]

    # -----------------------------------------
    # Sentiment research
    # -----------------------------------------

    if research_type == "sentiment":

        return [
            "sentiment"
        ]

    # -----------------------------------------
    # Portfolio risk
    # -----------------------------------------

    if research_type == "portfolio":

        return [
            "risk"
        ]

    # -----------------------------------------
    # Conceptual question
    # -----------------------------------------

    if research_type == "conceptual":

        return [
            "rag"
        ]

    # -----------------------------------------
    # Default
    # -----------------------------------------

    return [
        "fundamental",
        "sentiment",
        "risk"
    ]


# ==================================================
# CREATE GRAPH
# ==================================================

graph = StateGraph(
    ResearchState
)


# ==================================================
# ADD NODES
# ==================================================

graph.add_node(
    "supervisor",
    run_supervisor
)

graph.add_node(
    "fundamental",
    run_fundamental
)

graph.add_node(
    "sentiment",
    run_sentiment
)

graph.add_node(
    "risk",
    run_risk
)

graph.add_node(
    "rag",
    run_rag
)

graph.add_node(
    "report",
    generate_report
)


# ==================================================
# START → SUPERVISOR
# ==================================================

graph.add_edge(
    START,
    "supervisor"
)


# ==================================================
# SUPERVISOR → RESEARCH AGENTS
# ==================================================

graph.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "fundamental": "fundamental",
        "sentiment": "sentiment",
        "risk": "risk",
        "rag": "rag"
    }
)


# ==================================================
# RESEARCH AGENTS → REPORT
# ==================================================

graph.add_edge(
    "fundamental",
    "report"
)

graph.add_edge(
    "sentiment",
    "report"
)

graph.add_edge(
    "risk",
    "report"
)


# ==================================================
# RAG → END
# ==================================================

graph.add_edge(
    "rag",
    END
)


# ==================================================
# REPORT → END
# ==================================================

graph.add_edge(
    "report",
    END
)


# ==================================================
# COMPILE
# ==================================================

research_graph = graph.compile()


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    # -----------------------------------------
    # Test 1: Full research
    # -----------------------------------------

    initial_state = {

        "symbol": "TCS.NS",

        "question":
            "Give me a complete analysis of TCS",

        "portfolio_symbols": [
            "TCS.NS",
            "INFY.NS",
            "RELIANCE.NS"
        ],

        "portfolio_weights": [
            0.4,
            0.3,
            0.3
        ]
    }

    print("\n===================================")
    print(" STOCK RESEARCH ASSISTANT")
    print("===================================")

    result = research_graph.invoke(
        initial_state
    )

    print("\n===================================")
    print(" FINAL REPORT")
    print("===================================")

    print(
        result.get(
            "final_report"
        )
    )