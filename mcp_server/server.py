from mcp.server.fastmcp import FastMCP

from price_tool import get_price
from financial_tool import get_financials
from risk_tool import calc_portfolio_risk


mcp = FastMCP("Stock Research Assistant")


@mcp.tool()
def stock_price(symbol: str):
    """Get the latest available stock price."""
    return get_price(symbol)


@mcp.tool()
def company_financials(symbol: str):
    """Get basic company financial information."""
    return get_financials(symbol)


@mcp.tool()
def portfolio_risk(symbols: list[str], weights: list[float]):
    """Calculate portfolio return and annualized volatility."""
    return calc_portfolio_risk(symbols, weights)


if __name__ == "__main__":
    mcp.run()