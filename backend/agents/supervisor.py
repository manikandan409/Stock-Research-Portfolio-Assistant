from typing import TypedDict


class ResearchState(TypedDict, total=False):
    symbol: str
    question: str

    portfolio_symbols: list[str]
    portfolio_weights: list[float]

    research_type: str

    fundamental_data: dict
    sentiment_data: dict
    risk_data: dict
    rag_data: list
    final_report: dict


def supervisor(state: ResearchState):
    """
    Supervisor controls and classifies the research request.

    Research types:
    - conceptual       -> RAG
    - fundamental      -> Fundamental Agent
    - sentiment        -> Sentiment Agent
    - portfolio        -> Risk Agent
    - full_research    -> Fundamental + Sentiment + Risk
    """

    print("\n===================================")
    print("        SUPERVISOR AGENT")
    print("===================================")

    symbol = state.get("symbol")
    question = state.get("question", "")

    # -----------------------------------------
    # Validate stock symbol
    # -----------------------------------------

    if not symbol:
        print("[SUPERVISOR] Error: Stock symbol is missing.")

        return {
            "research_type": "error",
            "final_report": {
                "status": "error",
                "message": "Stock symbol is required."
            }
        }

    question_lower = question.lower()

    # -----------------------------------------
    # Conceptual / educational questions
    # -----------------------------------------

    conceptual_keywords = [
        "what is",
        "what does",
        "meaning of",
        "define",
        "definition",
        "explain",
        "explanation",
        "how does",
        "difference between",
        "concept of",
        "understand",
        "meaning"
    ]

    conceptual_finance_terms = [
        "p/e",
        "pe ratio",
        "p/b",
        "price to book",
        "eps",
        "roe",
        "debt-to-equity",
        "debt to equity",
        "market capitalization",
        "market cap",
        "dividend yield",
        "beta",
        "volatility",
        "diversification",
        "concentration risk",
        "annualized return",
        "free cash flow",
        "ebitda",
        "revenue growth",
        "financial ratio",
        "bull market",
        "bear market",
        "liquidity",
        "benchmark",
        "intrinsic value",
        "capital gain",
        "capital loss"
    ]

    is_conceptual = any(
        keyword in question_lower
        for keyword in conceptual_keywords
    )

    is_finance_concept = any(
        term in question_lower
        for term in conceptual_finance_terms
    )

    # -----------------------------------------
    # Fundamental research
    # -----------------------------------------

    fundamental_keywords = [
        "fundamental",
        "fundamentals",
        "financial",
        "finance",
        "revenue",
        "profit",
        "earnings",
        "valuation",
        "debt",
        "roe",
        "balance sheet",
        "financial statement"
    ]

    # -----------------------------------------
    # Sentiment / news research
    # -----------------------------------------

    sentiment_keywords = [
        "news",
        "sentiment",
        "latest news",
        "recent news",
        "announcement",
        "regulatory",
        "market news"
    ]

    # -----------------------------------------
    # Risk / portfolio research
    # -----------------------------------------

    risk_keywords = [
        "risk",
        "portfolio",
        "weight",
        "drawdown",
        "concentration"
    ]

    # -----------------------------------------
    # Portfolio analysis phrases
    # -----------------------------------------

    portfolio_analysis_keywords = [
        "calculate portfolio",
        "analyze portfolio",
        "analyse portfolio",
        "portfolio risk",
        "portfolio volatility",
        "portfolio beta",
        "portfolio concentration",
        "portfolio weight",
        "my portfolio",
        "holdings",
        "allocation"
    ]

    is_portfolio_analysis = any(
        keyword in question_lower
        for keyword in portfolio_analysis_keywords
    )

    # -----------------------------------------
    # Routing priority
    # -----------------------------------------
    #
    # 1. Actual portfolio/risk analysis
    # 2. Conceptual financial questions
    # 3. Fundamental research
    # 4. Sentiment research
    # 5. Full research
    #
    # This prevents:
    #
    # "What is beta?"
    #        -> conceptual
    #
    # while:
    #
    # "Calculate portfolio beta"
    #        -> portfolio
    #
    # -----------------------------------------

    if is_portfolio_analysis:
        research_type = "portfolio"

    elif is_conceptual and is_finance_concept:
        research_type = "conceptual"

    elif any(
        keyword in question_lower
        for keyword in risk_keywords
    ):
        research_type = "portfolio"

    elif any(
        keyword in question_lower
        for keyword in fundamental_keywords
    ):
        research_type = "fundamental"

    elif any(
        keyword in question_lower
        for keyword in sentiment_keywords
    ):
        research_type = "sentiment"

    else:
        research_type = "full_research"

    # -----------------------------------------
    # Display classification
    # -----------------------------------------

    print(f"[SUPERVISOR] Symbol       : {symbol}")
    print(f"[SUPERVISOR] Question     : {question}")
    print(f"[SUPERVISOR] Research type: {research_type}")

    return {
        "research_type": research_type
    }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    test_questions = [
        "Give me a complete analysis of TCS",
        "What are the fundamentals of TCS?",
        "What is the latest news about TCS?",
        "What is the risk of my portfolio?",
        "What does a P/E ratio of 35 mean?",
        "What is beta?",
        "Explain diversification",
        "What is debt-to-equity ratio?",
        "What is the meaning of market capitalization?",
        "What is volatility?",
        "Calculate portfolio beta",
        "Calculate portfolio volatility",
        "Analyze my portfolio risk",
        "What is the concentration of my holdings?"
    ]

    for question in test_questions:

        print("\n-----------------------------------")
        print("Question:", question)

        result = supervisor({
            "symbol": "TCS.NS",
            "question": question
        })

        print("Result:", result)