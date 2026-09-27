from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.graph.research_graph import research_graph
from backend.database import (
    save_research_report,
    get_research_history
)
from backend.agents.finance_qa_agent import finance_qa_agent

from mcp_server.price_tool import get_price
from mcp_server.financial_tool import get_financials


router = APIRouter()


# ==========================================
# REQUEST MODELS
# ==========================================

class ResearchRequest(BaseModel):
    symbol: str
    portfolio_symbols: list[str] = []
    portfolio_weights: list[float] = []


class FinanceQuestionRequest(BaseModel):
    question: str


# ==========================================
# RESEARCH API
# ==========================================

@router.post("/research")
def research_stock(request: ResearchRequest):

    try:

        # --------------------------------------
        # Clean stock symbol
        # --------------------------------------

        symbol = request.symbol.upper().strip()

        if not symbol:

            raise HTTPException(
                status_code=400,
                detail="Stock symbol is required."
            )

        # --------------------------------------
        # Portfolio handling
        # --------------------------------------

        if not request.portfolio_symbols:

            portfolio_symbols = [symbol]
            portfolio_weights = [1.0]

        else:

            portfolio_symbols = request.portfolio_symbols
            portfolio_weights = request.portfolio_weights

        # --------------------------------------
        # Validate portfolio
        # --------------------------------------

        if len(portfolio_symbols) != len(portfolio_weights):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Portfolio symbols and weights "
                    "must have the same length."
                )
            )

        # --------------------------------------
        # Initial LangGraph state
        # --------------------------------------

        initial_state = {

            "symbol": symbol,

            "portfolio_symbols": portfolio_symbols,

            "portfolio_weights": portfolio_weights

        }

        # --------------------------------------
        # Run LangGraph
        # --------------------------------------

        result = research_graph.invoke(initial_state)

        # --------------------------------------
        # Get final report
        # --------------------------------------

        report = result.get("final_report")

        if not report:

            raise HTTPException(
                status_code=500,
                detail="Research report was not generated."
            )

        # --------------------------------------
        # Add database information
        # --------------------------------------

        report["created_at"] = datetime.now().isoformat()

        report["portfolio"] = {

            "symbols": portfolio_symbols,

            "weights": portfolio_weights

        }

        # --------------------------------------
        # Save report to MongoDB
        # --------------------------------------

        report_id = save_research_report(report)

        # --------------------------------------
        # Return response
        # --------------------------------------

        return {

            "status": "success",

            "report_id": report_id,

            "report": report

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# RESEARCH HISTORY API
# ==========================================

@router.get("/history")
def research_history():

    try:

        history = get_research_history()

        return {

            "status": "success",

            "count": len(history),

            "history": history

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# FINANCE Q&A API
# ==========================================

@router.post("/finance-question")
def ask_finance_question(
    request: FinanceQuestionRequest
):

    try:

        question = request.question.strip()

        if not question:

            raise HTTPException(
                status_code=400,
                detail="Question is required."
            )

        result = finance_qa_agent(question)

        if result.get("status") == "error":

            raise HTTPException(
                status_code=500,
                detail=result.get(
                    "error",
                    "Finance Q&A failed."
                )
            )

        return result

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# PRICE HISTORY API
# ==========================================

@router.get("/price-history")
def price_history(
    symbol: str,
    period: str = "1mo"
):

    try:

        # --------------------------------------
        # Clean symbol
        # --------------------------------------

        symbol = symbol.upper().strip()

        if not symbol:

            raise HTTPException(
                status_code=400,
                detail="Stock symbol is required."
            )

        # --------------------------------------
        # Allowed periods
        # --------------------------------------

        allowed_periods = [
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y"
        ]

        if period not in allowed_periods:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid period. Use one of: "
                    + ", ".join(allowed_periods)
                )
            )

        # --------------------------------------
        # Get historical price data
        # --------------------------------------

        result = get_price(
            symbol,
            period
        )

        # --------------------------------------
        # Handle price tool error
        # --------------------------------------

        if result.get("error"):

            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )

        # --------------------------------------
        # Return price history
        # --------------------------------------

        return {

            "status": "success",

            "data": result

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# COMPANY COMPARISON API
# ==========================================

@router.get("/compare")
def compare_companies(
    symbol1: str,
    symbol2: str
):

    try:

        # --------------------------------------
        # Clean symbols
        # --------------------------------------

        symbol1 = symbol1.upper().strip()
        symbol2 = symbol2.upper().strip()

        # --------------------------------------
        # Validate symbols
        # --------------------------------------

        if not symbol1 or not symbol2:

            raise HTTPException(
                status_code=400,
                detail="Both company symbols are required."
            )

        # --------------------------------------
        # Prevent same-company comparison
        # --------------------------------------

        if symbol1 == symbol2:

            raise HTTPException(
                status_code=400,
                detail="Please select two different companies."
            )

        # --------------------------------------
        # Get financial data
        # --------------------------------------

        company1 = get_financials(symbol1)
        company2 = get_financials(symbol2)

        # --------------------------------------
        # Check company 1
        # --------------------------------------

        if "error" in company1:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Could not retrieve data for "
                    f"{symbol1}: {company1['error']}"
                )
            )

        # --------------------------------------
        # Check company 2
        # --------------------------------------

        if "error" in company2:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Could not retrieve data for "
                    f"{symbol2}: {company2['error']}"
                )
            )

        # --------------------------------------
        # Metrics to compare
        # --------------------------------------

        metrics = [

            "company_name",

            "sector",

            "industry",

            "date",

            "close",

            "market_cap",

            "pe_ratio",

            "forward_pe",

            "price_to_book",

            "profit_margin",

            "revenue_growth",

            "return_on_equity",

            "debt_to_equity",

            "dividend_yield"

        ]

        # --------------------------------------
        # Build comparison
        # --------------------------------------

        comparison = {}

        for metric in metrics:

            comparison[metric] = {

                symbol1: company1.get(metric),

                symbol2: company2.get(metric)

            }

        # --------------------------------------
        # Return comparison
        # --------------------------------------

        return {

            "status": "success",

            "symbol1": symbol1,

            "symbol2": symbol2,

            "comparison": comparison

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )