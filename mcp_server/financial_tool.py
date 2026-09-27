import yfinance as yf


def get_financials(symbol: str):
    """
    Get basic financial information and latest market data
    for a company using Yahoo Finance.
    """

    try:

        # ==========================================
        # CREATE TICKER
        # ==========================================

        stock = yf.Ticker(symbol)

        info = stock.info


        # ==========================================
        # GET LATEST MARKET DATA
        # ==========================================

        history = stock.history(
            period="5d",
            auto_adjust=False
        )

        market_data = {}

        if not history.empty:

            latest = history.iloc[-1]

            latest_date = history.index[-1]

            market_data = {
                "date": latest_date.strftime(
                    "%Y-%m-%d"
                ),

                "open": float(
                    latest["Open"]
                ),

                "high": float(
                    latest["High"]
                ),

                "low": float(
                    latest["Low"]
                ),

                "close": float(
                    latest["Close"]
                ),

                "volume": int(
                    latest["Volume"]
                )
            }


        # ==========================================
        # RETURN DATA
        # ==========================================

        return {

            "symbol": symbol,

            # Company information
            "company_name": info.get(
                "longName"
            ),

            "sector": info.get(
                "sector"
            ),

            "industry": info.get(
                "industry"
            ),

            # Fundamental metrics
            "market_cap": info.get(
                "marketCap"
            ),

            "pe_ratio": info.get(
                "trailingPE"
            ),

            "forward_pe": info.get(
                "forwardPE"
            ),

            "price_to_book": info.get(
                "priceToBook"
            ),

            "profit_margin": info.get(
                "profitMargins"
            ),

            "revenue_growth": info.get(
                "revenueGrowth"
            ),

            "return_on_equity": info.get(
                "returnOnEquity"
            ),

            "debt_to_equity": info.get(
                "debtToEquity"
            ),

            "dividend_yield": info.get(
                "dividendYield"
            ),

            # Latest market data
            "date": market_data.get(
                "date"
            ),

            "open": market_data.get(
                "open"
            ),

            "high": market_data.get(
                "high"
            ),

            "low": market_data.get(
                "low"
            ),

            "close": market_data.get(
                "close"
            ),

            "volume": market_data.get(
                "volume"
            )
        }


    except Exception as e:

        return {
            "symbol": symbol,
            "error": str(e)
        }


# ==========================================
# DIRECT TEST
# ==========================================

if __name__ == "__main__":

    result = get_financials(
        "TCS.NS"
    )

    print("\n==============================")
    print(" FINANCIAL MCP TOOL")
    print("==============================")

    print(result)