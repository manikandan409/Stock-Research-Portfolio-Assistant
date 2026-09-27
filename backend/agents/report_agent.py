# backend/agents/report_agent.py

from datetime import datetime


# ==================================================
# REPORT AGENT
# ==================================================

def report_agent(
    symbol: str,
    fundamental_data: dict,
    sentiment_data: dict,
    risk_data: dict
):

    # ==================================================
    # BASIC INFORMATION
    # ==================================================

    today = datetime.now().strftime("%Y-%m-%d")

    financials = fundamental_data.get(
        "financial_data",
        {}
    )

    rag_research = fundamental_data.get(
        "rag_research",
        []
    )

    # ==================================================
    # COMPANY NAME
    # ==================================================

    company_name = (
        financials.get("company_name")
        or symbol
    )

    # Fix common formatting issues.
    company_name = (
        company_name
        .replace(
            "ConsultancyServices",
            "Consultancy Services"
        )
        .replace(
            "TataConsultancy",
            "Tata Consultancy"
        )
    )

    sector = financials.get(
        "sector",
        "Not available"
    )

    industry = financials.get(
        "industry",
        "Not available"
    )

    # ==================================================
    # MARKET SNAPSHOT
    # ==================================================

    market_snapshot = {

        "symbol": symbol,

        "date": financials.get(
            "date",
            "Not available"
        ),

        "open": financials.get(
            "open",
            "Not available"
        ),

        "high": financials.get(
            "high",
            "Not available"
        ),

        "low": financials.get(
            "low",
            "Not available"
        ),

        "close": financials.get(
            "close",
            "Not available"
        ),

        "volume": financials.get(
            "volume",
            "Not available"
        )
    }

    # ==================================================
    # BUSINESS OVERVIEW
    # ==================================================

    business_overview = {

        "company_name": company_name,

        "sector": sector,

        "industry": industry
    }

    # ==================================================
    # FINANCIAL FUNDAMENTALS
    # ==================================================

    financial_fundamentals = {

        "market_cap":
            financials.get(
                "market_cap",
                "Not available"
            ),

        "pe_ratio":
            financials.get(
                "pe_ratio",
                "Not available"
            ),

        "forward_pe":
            financials.get(
                "forward_pe",
                "Not available"
            ),

        "price_to_book":
            financials.get(
                "price_to_book",
                "Not available"
            ),

        "profit_margin":
            financials.get(
                "profit_margin",
                "Not available"
            ),

        "revenue_growth":
            financials.get(
                "revenue_growth",
                "Not available"
            ),

        "return_on_equity":
            financials.get(
                "return_on_equity",
                "Not available"
            ),

        "debt_to_equity":
            financials.get(
                "debt_to_equity",
                "Not available"
            ),

        "dividend_yield":
            financials.get(
                "dividend_yield",
                "Not available"
            )
    }

    # ==================================================
    # ANNUAL REPORT / RAG RESEARCH
    # ==================================================

    annual_report_research = []

    for item in rag_research:

        annual_report_research.append({

            "source":
                item.get(
                    "source",
                    "Unknown"
                ),

            "page":
                item.get(
                    "page",
                    "Unknown"
                ),

            "content":
                item.get(
                    "content",
                    ""
                )
        })

    # ==================================================
    # NEWS / SENTIMENT
    # ==================================================

    sentiment_summary = {}

    news_articles = []

    if isinstance(sentiment_data, dict):

        sentiment_summary = sentiment_data.get(
            "sentiment_summary",
            {}
        )

        news_data = sentiment_data.get(
            "news",
            {}
        )

        if isinstance(news_data, dict):

            news_articles = news_data.get(
                "results",
                []
            )

    # --------------------------------------------------
    # Build clean news evidence
    # --------------------------------------------------

    classified_news = []

    for article in news_articles:

        classified_news.append({

            "title":
                article.get(
                    "title",
                    "Unknown"
                ),

            "url":
                article.get(
                    "url",
                    None
                ),

            "published_date":
                article.get(
                    "published_date",
                    "Unknown"
                ),

            "sentiment":
                article.get(
                    "sentiment",
                    "neutral"
                ),

            "evidence":
                article.get(
                    "evidence",
                    ""
                ),

            "positive_signal_count":
                article.get(
                    "positive_signal_count",
                    0
                ),

            "negative_signal_count":
                article.get(
                    "negative_signal_count",
                    0
                )
        })

    # --------------------------------------------------
    # Final news sentiment section
    # --------------------------------------------------

    recent_news = {

        "agent":
            sentiment_data.get(
                "agent",
                "sentiment_agent"
            )
            if isinstance(sentiment_data, dict)
            else "sentiment_agent",

        "company":
            sentiment_data.get(
                "company",
                symbol
            )
            if isinstance(sentiment_data, dict)
            else symbol,

        "status":
            sentiment_data.get(
                "status",
                "unknown"
            )
            if isinstance(sentiment_data, dict)
            else "unknown",

        "sentiment_summary": {

            "overall_sentiment":
                sentiment_summary.get(
                    "overall_sentiment",
                    "Not available"
                ),

            "articles_analyzed":
                sentiment_summary.get(
                    "articles_analyzed",
                    len(classified_news)
                ),

            "positive_articles":
                sentiment_summary.get(
                    "positive_articles",
                    0
                ),

            "negative_articles":
                sentiment_summary.get(
                    "negative_articles",
                    0
                ),

            "mixed_articles":
                sentiment_summary.get(
                    "mixed_articles",
                    0
                ),

            "neutral_articles":
                sentiment_summary.get(
                    "neutral_articles",
                    0
                )
        },

        "news_articles":
            classified_news
    }

    # ==================================================
    # NEWS DATE INFORMATION
    # ==================================================

    news_dates = []

    for article in classified_news:

        published_date = article.get(
            "published_date"
        )

        if published_date:

            news_dates.append(
                published_date
            )

    # ==================================================
    # PORTFOLIO RISK
    # ==================================================

    portfolio_risk = risk_data

    # ==================================================
    # RISK DATA PERIOD
    # ==================================================

    risk_data_period = "Not available"

    if isinstance(risk_data, dict):

        risk_analysis = risk_data.get(
            "analysis",
            {}
        )

        if isinstance(
            risk_analysis,
            dict
        ):

            risk_data_period = risk_analysis.get(
                "data_period",
                "Not available"
            )

    # ==================================================
    # DATA SOURCES
    # ==================================================

    data_sources = []

    if financials:

        data_sources.append(
            "Yahoo Finance"
        )

    if sentiment_data:

        data_sources.append(
            "Tavily News Search"
        )

    if rag_research:

        rag_sources = set()

        for item in rag_research:

            source = item.get(
                "source"
            )

            if source:

                rag_sources.add(
                    source
                )

        for source in sorted(
            rag_sources
        ):

            data_sources.append(
                f"RAG: {source}"
            )

    if not data_sources:

        data_sources.append(
            "No external data source available"
        )

    # ==================================================
    # OPEN QUESTIONS
    # ==================================================

    open_questions = [

        "How sustainable are the reported revenue and profit growth trends across future reporting periods?",

        "How might changes in global technology spending affect future business performance?",

        "How could changes in regulatory, geopolitical or cross-border operating conditions affect the company?",

        "How do the company's current valuation ratios compare with relevant industry peers and historical levels?",

        "What additional information from future annual reports and earnings announcements could materially change the research assessment?"
    ]

    # ==================================================
    # LIMITATIONS
    # ==================================================

    limitations = []

    if not rag_research:

        limitations.append(
            "No company-specific RAG document "
            "was available for this research."
        )

    if not sentiment_data:

        limitations.append(
            "No sentiment or news data "
            "was available."
        )

    if not risk_data:

        limitations.append(
            "Portfolio risk analysis "
            "was not available."
        )

    limitations.append(
        "Market prices and financial metrics "
        "may change over time."
    )

    limitations.append(
        "News search results depend on the "
        "availability, timing and relevance "
        "of external sources."
    )

    limitations.append(
        "Historical financial and market data "
        "does not by itself establish future performance."
    )

    # ==================================================
    # DATA PERIOD
    # ==================================================

    annual_report_period = "Not available"

    if rag_research:

        annual_report_period = (
            "Company annual report data available "
            "in the RAG knowledge base"
        )

    data_period = {

        "report_generated_date":
            today,

        "market_data_date":
            market_snapshot.get(
                "date",
                "Not available"
            ),

        "risk_analysis_period":
            risk_data_period,

        "annual_report_period":
            annual_report_period,

        "news_dates_available":
            news_dates
    }

    # ==================================================
    # DISCLAIMER
    # ==================================================

    disclaimer = (
        "This report is for educational and research "
        "purposes only. It is not investment advice "
        "or a recommendation to buy or sell any security. "
        "Financial information may change over time "
        "and should be independently verified."
    )

    # ==================================================
    # FINAL REPORT
    # ==================================================

    report = {

        "report_title":
            f"Stock Research Report - {symbol}",

        "company":
            symbol,

        "company_name":
            company_name,

        "report_generated_date":
            today,

        "market_snapshot":
            market_snapshot,

        "business_overview":
            business_overview,

        "financial_fundamentals":
            financial_fundamentals,

        "annual_report_research":
            annual_report_research,

        "recent_news":
            recent_news,

        "portfolio_risk":
            portfolio_risk,

        "open_questions":
            open_questions,

        "data_period":
            data_period,

        "data_sources":
            data_sources,

        "limitations":
            limitations,

        "disclaimer":
            disclaimer
    }

    return report