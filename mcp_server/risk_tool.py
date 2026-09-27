import yfinance as yf
import numpy as np
import pandas as pd


def calc_portfolio_risk(symbols, weights):
    """
    Calculate portfolio risk using historical returns.

    Calculates:
    - Annualized return
    - Annualized volatility
    - Portfolio beta
    - Concentration using Herfindahl-Hirschman Index (HHI)

    symbols example:
    ["TCS.NS", "INFY.NS", "RELIANCE.NS"]

    weights example:
    [0.4, 0.3, 0.3]
    """

    try:
        # -----------------------------
        # Validate inputs
        # -----------------------------
        if len(symbols) != len(weights):
            return {
                "error": "Number of symbols and weights must be equal"
            }

        if len(symbols) == 0:
            return {
                "error": "At least one symbol is required"
            }

        if any(weight < 0 for weight in weights):
            return {
                "error": "Portfolio weights cannot be negative"
            }

        if not np.isclose(sum(weights), 1.0):
            return {
                "error": "Portfolio weights must add up to 1.0"
            }

        # -----------------------------
        # Download portfolio data
        # -----------------------------
        data = yf.download(
            symbols,
            period="1y",
            auto_adjust=True,
            progress=False
        )["Close"]

        if data.empty:
            return {
                "error": "No historical price data found"
            }

        # If only one symbol is returned, convert to DataFrame
        if isinstance(data, pd.Series):
            data = data.to_frame(name=symbols[0])

        data = data.dropna()

        if data.empty:
            return {
                "error": "No usable historical price data found"
            }

        # -----------------------------
        # Calculate daily returns
        # -----------------------------
        returns = data.pct_change().dropna()

        if returns.empty:
            return {
                "error": "Not enough historical data to calculate risk"
            }

        weights_array = np.array(weights, dtype=float)

        # Make sure columns follow requested symbol order
        available_symbols = [
            symbol for symbol in symbols
            if symbol in returns.columns
        ]

        if len(available_symbols) != len(symbols):
            missing_symbols = [
                symbol for symbol in symbols
                if symbol not in returns.columns
            ]

            return {
                "error": f"Missing price data for: {missing_symbols}"
            }

        returns = returns[symbols]

        # -----------------------------
        # Portfolio returns
        # -----------------------------
        portfolio_returns = returns.dot(weights_array)

        # -----------------------------
        # Annualized volatility
        # -----------------------------
        daily_volatility = portfolio_returns.std()

        annualized_volatility = (
            daily_volatility * np.sqrt(252)
        )

        # -----------------------------
        # Annualized return
        # -----------------------------
        average_daily_return = portfolio_returns.mean()

        annualized_return = (
            average_daily_return * 252
        )

        # -----------------------------
        # Portfolio beta
        #
        # Benchmark: NIFTY 50
        # Yahoo Finance ticker: ^NSEI
        # -----------------------------
        benchmark = yf.download(
            "^NSEI",
            period="1y",
            auto_adjust=True,
            progress=False
        )["Close"]

        if isinstance(benchmark, pd.DataFrame):
            benchmark = benchmark.iloc[:, 0]

        benchmark_returns = benchmark.pct_change().dropna()

        combined = pd.concat(
            [
                portfolio_returns.rename("portfolio"),
                benchmark_returns.rename("benchmark")
            ],
            axis=1
        ).dropna()

        if len(combined) > 1:
            covariance = np.cov(
                combined["portfolio"],
                combined["benchmark"]
            )[0][1]

            benchmark_variance = np.var(
                combined["benchmark"]
            )

            if benchmark_variance != 0:
                portfolio_beta = (
                    covariance / benchmark_variance
                )
            else:
                portfolio_beta = None
        else:
            portfolio_beta = None

        # -----------------------------
        # Concentration
        #
        # HHI = sum(weight^2)
        #
        # Lower value = more diversified
        # Higher value = more concentrated
        # -----------------------------
        hhi = np.sum(weights_array ** 2)

        effective_number_of_holdings = (
            1 / hhi
        )

        largest_weight = max(weights)

        # -----------------------------
        # Individual holding details
        # -----------------------------
        holding_details = []

        for symbol, weight in zip(symbols, weights):
            holding_details.append({
                "symbol": symbol,
                "weight": round(weight * 100, 2)
            })

        # -----------------------------
        # Final result
        # -----------------------------
        return {
            "symbols": symbols,
            "weights": weights,

            "annualized_return": round(
                float(annualized_return * 100),
                2
            ),

            "annualized_volatility": round(
                float(annualized_volatility * 100),
                2
            ),

            "portfolio_beta": (
                round(float(portfolio_beta), 2)
                if portfolio_beta is not None
                else None
            ),

            "concentration": {
                "hhi": round(float(hhi), 4),
                "effective_number_of_holdings": round(
                    float(effective_number_of_holdings),
                    2
                ),
                "largest_holding_weight": round(
                    float(largest_weight * 100),
                    2
                )
            },

            "holding_details": holding_details,

            "benchmark": "NIFTY 50 (^NSEI)",
            "data_period": "1 year",
            "trading_days": len(returns)
        }

    except Exception as e:
        return {
            "error": str(e)
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

    result = calc_portfolio_risk(
        symbols,
        weights
    )

    print("\n==============================")
    print(" PORTFOLIO RISK TOOL")
    print("==============================")

    print(result)