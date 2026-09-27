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

from mcp_server.financial_tool import get_financials
from rag.retriever import search_knowledge_base


# ==================================================
# FUNDAMENTAL AGENT
# ==================================================

def fundamental_agent(symbol: str):

    financials = get_financials(symbol)

    if "error" in financials:
        return {
            "agent": "fundamental_agent",
            "symbol": symbol,
            "status": "error",
            "data": financials
        }

    company_name = financials.get("company_name") or symbol

    # -----------------------------------------
    # RAG Query
    # -----------------------------------------

    rag_query = f"""
    {company_name} {symbol}
    revenue financial performance
    profit operating income
    annual report
    """

    rag_results = search_knowledge_base(
        rag_query,
        company_name=company_name
    )

    # -----------------------------------------
    # Prepare RAG Research
    # -----------------------------------------

    research_sources = []

    for result in rag_results:
        research_sources.append({
            "source": result.get("source"),
            "page": result.get("page"),
            "content": result.get("content")
        })

    # -----------------------------------------
    # Return Fundamental Data
    # -----------------------------------------

    return {
        "agent": "fundamental_agent",
        "symbol": symbol,
        "status": "success",

        "financial_data": {

            # Company information
            "company_name": financials.get("company_name"),
            "sector": financials.get("sector"),
            "industry": financials.get("industry"),

            # Market snapshot
            "date": financials.get("date"),
            "open": financials.get("open"),
            "high": financials.get("high"),
            "low": financials.get("low"),
            "close": financials.get("close"),
            "volume": financials.get("volume"),

            # Fundamental metrics
            "market_cap": financials.get("market_cap"),
            "pe_ratio": financials.get("pe_ratio"),
            "forward_pe": financials.get("forward_pe"),
            "price_to_book": financials.get("price_to_book"),
            "profit_margin": financials.get("profit_margin"),
            "revenue_growth": financials.get("revenue_growth"),
            "return_on_equity": financials.get("return_on_equity"),
            "debt_to_equity": financials.get("debt_to_equity"),
            "dividend_yield": financials.get("dividend_yield")
        },

        "rag_research": research_sources
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    result = fundamental_agent("TCS.NS")

    print("\n==============================")
    print(" FUNDAMENTAL AGENT")
    print("==============================")

    print("\n--- Financial Data ---")
    print(result["financial_data"])

    print("\n--- RAG Research ---")
    print(result["rag_research"])