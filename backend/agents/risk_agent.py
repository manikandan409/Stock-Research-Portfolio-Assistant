import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)

from mcp_server.risk_tool import calc_portfolio_risk


def risk_agent(symbols: list[str], weights: list[float]):
    """
    Analyze portfolio risk using historical market data.
    """

    result = calc_portfolio_risk(symbols, weights)

    if "error" in result:
        return {
            "agent": "risk_agent",
            "status": "error",
            "data": result
        }

    return {
        "agent": "risk_agent",
        "status": "success",
        "analysis": result
    }


if __name__ == "__main__":

    symbols = [
        "TCS.NS",
        "INFY.NS",
        "RELIANCE.NS"
    ]

    weights = [
        0.4,
        0.3,
        0.3
    ]

    print(risk_agent(symbols, weights))