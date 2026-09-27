import yfinance as yf


def get_price(symbol: str, period: str = "5d"):
    try:
        stock = yf.Ticker(symbol)

        data = stock.history(
            period=period,
            auto_adjust=False
        )

        if data.empty:
            return {
                "symbol": symbol,
                "error": "No price data found"
            }

        latest = data.iloc[-1]

        historical_prices = []

        for index, row in data.iterrows():

            historical_prices.append({
                "date": str(index.date()),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"])
            })

        return {
            "symbol": symbol,
            "period": period,

            "date": str(data.index[-1].date()),

            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "close": round(float(latest["Close"]), 2),
            "volume": int(latest["Volume"]),

            "historical_prices": historical_prices
        }

    except Exception as e:

        return {
            "symbol": symbol,
            "error": str(e)
        }


if __name__ == "__main__":

    result = get_price(
        "TCS.NS",
        "1mo"
    )

    print(result)