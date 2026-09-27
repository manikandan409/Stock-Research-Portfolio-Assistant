import re
from datetime import datetime

from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

tavily = TavilySearch(
    max_results=5,
    topic="news"
)


# Simple finance-news sentiment vocabulary.
# This is intentionally deterministic so testing does not consume an LLM request.
POSITIVE_WORDS = {
    "growth",
    "gain",
    "gains",
    "positive",
    "profit",
    "profits",
    "increase",
    "increased",
    "improved",
    "improvement",
    "strong",
    "stronger",
    "rise",
    "rises",
    "rising",
    "up",
    "higher",
    "beat",
    "beats",
    "surge",
    "surged",
    "bullish",
    "outperform",
    "outperformed",
    "upgrade",
    "upgraded",
    "record",
    "expansion",
}

NEGATIVE_WORDS = {
    "loss",
    "losses",
    "decline",
    "declined",
    "decrease",
    "decreased",
    "negative",
    "weak",
    "weaker",
    "fall",
    "falls",
    "fell",
    "falling",
    "down",
    "lower",
    "miss",
    "missed",
    "drop",
    "dropped",
    "risk",
    "risks",
    "concern",
    "concerns",
    "crisis",
    "cut",
    "cuts",
    "downgrade",
    "downgraded",
    "uncertainty",
    "pressure",
    "pressures",
}


def classify_sentiment(text: str):
    """
    Deterministic finance-news sentiment classification.

    Returns:
        positive / negative / neutral / mixed
    """

    if not text:
        return "neutral", 0, 0

    words = set(
        re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower()
        )
    )

    positive_count = len(words.intersection(POSITIVE_WORDS))
    negative_count = len(words.intersection(NEGATIVE_WORDS))

    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    elif positive_count == 0 and negative_count == 0:
        sentiment = "neutral"
    else:
        sentiment = "mixed"

    return sentiment, positive_count, negative_count


def sentiment_agent(company: str):
    """
    Search company news through Tavily and classify each result.

    No LLM request is used here.
    """

    try:
        results = tavily.invoke({
            "query": f"{company} latest news earnings regulatory developments"
        })

        raw_results = results.get("results", [])

        classified_results = []

        positive_articles = 0
        negative_articles = 0
        neutral_articles = 0
        mixed_articles = 0

        for article in raw_results:

            title = article.get("title", "")
            content = article.get("content", "")
            published_date = article.get(
                "published_date",
                "Unknown"
            )

            combined_text = f"{title} {content}"

            sentiment, positive_count, negative_count = (
                classify_sentiment(combined_text)
            )

            if sentiment == "positive":
                positive_articles += 1
            elif sentiment == "negative":
                negative_articles += 1
            elif sentiment == "mixed":
                mixed_articles += 1
            else:
                neutral_articles += 1

            classified_results.append({
                "title": title,
                "url": article.get("url"),
                "published_date": published_date,
                "sentiment": sentiment,
                "positive_signal_count": positive_count,
                "negative_signal_count": negative_count,
                "evidence": content
            })

        # Determine overall news sentiment.
        if positive_articles > negative_articles:
            overall_sentiment = "positive"
        elif negative_articles > positive_articles:
            overall_sentiment = "negative"
        elif (
            positive_articles == negative_articles
            and positive_articles > 0
        ):
            overall_sentiment = "mixed"
        else:
            overall_sentiment = "neutral"

        return {
            "agent": "sentiment_agent",
            "company": company,
            "status": "success",

            "sentiment_summary": {
                "overall_sentiment": overall_sentiment,
                "articles_analyzed": len(classified_results),
                "positive_articles": positive_articles,
                "negative_articles": negative_articles,
                "mixed_articles": mixed_articles,
                "neutral_articles": neutral_articles,
            },

            "news": {
                "query": results.get("query"),
                "results": classified_results
            }
        }

    except Exception as e:

        return {
            "agent": "sentiment_agent",
            "company": company,
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":

    result = sentiment_agent("TCS.NS")

    print("\n===================================")
    print(" SENTIMENT AGENT TEST")
    print("===================================")

    print("\nOverall Sentiment:")
    print(
        result.get(
            "sentiment_summary",
            {}
        ).get(
            "overall_sentiment",
            "Not available"
        )
    )

    print("\nArticle Results:")

    for article in result.get(
        "news",
        {}
    ).get(
        "results",
        []
    ):

        print("\n-----------------------------------")
        print("Title:", article.get("title"))
        print("Date:", article.get("published_date"))
        print("Sentiment:", article.get("sentiment"))
        print("Evidence:", article.get("evidence", "")[:300])