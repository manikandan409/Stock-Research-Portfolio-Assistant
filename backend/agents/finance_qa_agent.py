import os
import json
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
import yfinance as yf

from rag.retriever import search_knowledge_base

load_dotenv()


# ============================================================
# API KEYS
# ============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_DAILY_LIMIT = int(os.getenv("GROQ_DAILY_LIMIT", "10"))

GROQ_USAGE_FILE = os.path.join(
    os.path.dirname(__file__),
    "groq_usage.json"
)


# ============================================================
# COMPANY KEYWORDS
# ============================================================

COMPANY_KEYWORDS = {
    "reliance industries": "Reliance",
    "reliance industries limited": "Reliance",
    "reliance": "Reliance",

    "tata consultancy services": "TCS",
    "tata consultancy": "TCS",
    "tcs": "TCS",

    "infosys": "Infosys",

    "hdfc bank": "HDFC Bank",
    "hdfc": "HDFC Bank",

    "icici bank": "ICICI Bank",
    "icici": "ICICI Bank",

    "wipro": "Wipro",

    "bharti airtel": "Airtel",
    "airtel": "Airtel",

    "itc": "ITC",

    "adani enterprises": "Adani Enterprises",
    "adani": "Adani Enterprises",

    "larsen & toubro": "Larsen & Toubro",
    "larsen": "Larsen & Toubro",
    "l&t": "Larsen & Toubro",

    "state bank of india": "State Bank of India",
    "sbi": "State Bank of India",

    "axis bank": "Axis Bank",
    "axis": "Axis Bank",

    "maruti suzuki": "Maruti Suzuki",
    "maruti": "Maruti Suzuki",

    "tata motors": "Tata Motors",

    "tata steel": "Tata Steel",

    "hindalco": "Hindalco",

    "sun pharmaceutical": "Sun Pharmaceutical",
    "sun pharma": "Sun Pharmaceutical",
}


# ============================================================
# TICKER MAPPING
# ============================================================

COMPANY_TICKERS = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Wipro": "WIPRO.NS",
    "Airtel": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Larsen & Toubro": "LT.NS",
    "State Bank of India": "SBIN.NS",
    "Axis Bank": "AXISBANK.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Hindalco": "HINDALCO.NS",
    "Sun Pharmaceutical": "SUNPHARMA.NS",
}


# ============================================================
# COMPANY SEARCH RULES
# ============================================================

COMPANY_SEARCH_RULES = {
    "Reliance": {
        "required": [
            "reliance industries",
            "reliance industries limited",
            "ril",
            "reliance.com",
            "ril.com",
            "reliance annual report",
            "reliance jio",
            "reliance retail",
        ],
        "blocked": [
            "reliance steel",
            "reliance steel & aluminum",
            "reliance worldwide",
            "reliance worldwide corporation",
            "reliance global group",
            "reliance infrastructure",
            "reliance power",
            "reliance naval",
        ],
    }
}


# ============================================================
# PREFERRED SOURCES
# ============================================================

PREFERRED_DOMAINS = [
    "reuters.com",
    "economictimes.indiatimes.com",
    "m.economictimes.com",
    "moneycontrol.com",
    "business-standard.com",
    "livemint.com",
    "thehindubusinessline.com",
    "bloomberg.com",
    "cnbctv18.com",
    "nseindia.com",
    "bseindia.com",
    "reliance.com",
]


# ============================================================
# COMPANY DETECTION
# ============================================================

def detect_company(question: str) -> Optional[str]:

    question_lower = question.lower()

    sorted_keywords = sorted(
        COMPANY_KEYWORDS.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for keyword, company in sorted_keywords:

        if keyword in question_lower:
            return company

    return None


# ============================================================
# LATEST NEWS DETECTION
# ============================================================

def is_latest_news_question(question: str) -> bool:

    question_lower = question.lower()

    latest_words = [
        "latest news",
        "latest",
        "recent news",
        "recent",
        "new developments",
        "recent developments",
        "what happened recently",
        "current news",
        "current developments",
        "recent update",
        "latest update",
        "today's news",
        "today news",
    ]

    return any(
        word in question_lower
        for word in latest_words
    )


# ============================================================
# DATE PARSER
# ============================================================

def parse_result_date(result: dict):

    date_value = (
        result.get("published_date")
        or result.get("published")
        or result.get("date")
    )

    if not date_value:
        return None

    try:

        date_string = str(date_value)

        if date_string.endswith("Z"):
            date_string = date_string[:-1]

        parsed = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except Exception:

        # Try common RFC style date
        formats = [
            "%a, %d %b %Y %H:%M:%S GMT",
            "%a, %d %b %Y %H:%M:%S %z",
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    str(date_value),
                    fmt
                ).replace(tzinfo=timezone.utc)

            except Exception:
                pass

    return None


# ============================================================
# COMPANY RESULT VALIDATION
# ============================================================

def validate_company_result(
    result: dict,
    company_name: str
) -> bool:

    title = str(
        result.get("title")
        or result.get("source")
        or ""
    ).lower()

    content = str(
        result.get("content")
        or ""
    ).lower()

    url = str(
        result.get("url")
        or ""
    ).lower()

    combined = (
        title
        + " "
        + content
        + " "
        + url
    )

    rules = COMPANY_SEARCH_RULES.get(
        company_name
    )

    if not rules:

        return True

    # Reject unrelated Reliance companies
    for blocked in rules["blocked"]:

        if blocked in combined:
            return False

    # Require a meaningful company reference
    for required in rules["required"]:

        if required in combined:
            return True

    return False


# ============================================================
# NEWS RESULT SCORING
# ============================================================

def score_news_result(
    result: dict,
    company_name: str
):

    score = 0

    title = str(
        result.get("title")
        or result.get("source")
        or ""
    ).lower()

    content = str(
        result.get("content")
        or ""
    ).lower()

    url = str(
        result.get("url")
        or ""
    ).lower()

    combined = (
        title
        + " "
        + content
        + " "
        + url
    )

    # --------------------------------------------------------
    # Company relevance
    # --------------------------------------------------------

    if company_name.lower() in title:
        score += 20

    if company_name.lower() in content:
        score += 10

    # Special Reliance handling
    if company_name == "Reliance":

        if "reliance industries" in combined:
            score += 25

        if "ril" in combined:
            score += 10

        if "reliance jio" in combined:
            score += 8

        if "reliance retail" in combined:
            score += 8

    # --------------------------------------------------------
    # Preferred source
    # --------------------------------------------------------

    for domain in PREFERRED_DOMAINS:

        if domain in url:
            score += 15
            break

    # --------------------------------------------------------
    # Recency
    # --------------------------------------------------------

    result_date = parse_result_date(result)

    if result_date:

        now = datetime.now(timezone.utc)

        age_days = (
            now - result_date
        ).days

        if age_days <= 7:
            score += 40

        elif age_days <= 14:
            score += 30

        elif age_days <= 30:
            score += 20

        elif age_days <= 90:
            score += 8

        elif age_days <= 180:
            score += 2

        else:
            score -= 15

    else:

        score -= 10

    return score


# ============================================================
# TAVILY SEARCH
# ============================================================

def search_web(
    question: str,
    company_name: Optional[str] = None,
    latest_news: bool = False
):

    if not TAVILY_API_KEY:

        print("TAVILY_API_KEY not found.")

        return []

    if latest_news and company_name:

        if company_name == "Reliance":

            query = (
                '"Reliance Industries" '
                'OR "Reliance Industries Limited" '
                'latest news recent developments '
                'announcements September 2026 '
                'RIL RIL.com'
            )

        else:

            query = (
                f'"{company_name}" '
                f'latest news recent developments '
                f'announcements September 2026'
            )

    else:

        query = question

    print("Tavily query:", query)

    try:

        search = TavilySearch(
            max_results=10,
            topic="news" if latest_news else "general",
            tavily_api_key=TAVILY_API_KEY
        )

        response = search.invoke(query)

    except Exception as e:

        print("Tavily error:", e)

        return []

    # Tavily can return a dictionary
    if isinstance(response, dict):

        results = response.get(
            "results",
            []
        )

    else:

        results = []

    print(
        "Tavily raw results:",
        len(results)
    )

    cleaned_results = []

    for result in results:

        if not isinstance(result, dict):
            continue

        title = result.get(
            "title",
            ""
        )

        content = result.get(
            "content",
            ""
        )

        url = result.get(
            "url",
            ""
        )

        published_date = (
            result.get("published_date")
            or result.get("published")
            or result.get("date")
        )

        cleaned = {
            "type": "Web",
            "source": title,
            "content": content,
            "url": url,
            "published_date": published_date,
        }

        # ----------------------------------------------------
        # Validate company
        # ----------------------------------------------------

        if company_name:

            if not validate_company_result(
                cleaned,
                company_name
            ):

                print(
                    "Rejected unrelated source:",
                    title
                )

                continue

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        if latest_news and company_name:

            cleaned["_score"] = score_news_result(
                cleaned,
                company_name
            )

        cleaned_results.append(cleaned)

    # --------------------------------------------------------
    # Latest-news sorting
    # --------------------------------------------------------

    if latest_news:

        cleaned_results.sort(
            key=lambda x: (
                x.get("_score", 0),
                parse_result_date(x)
                or datetime.min.replace(
                    tzinfo=timezone.utc
                )
            ),
            reverse=True
        )

        # Only retain the strongest 5 results
        cleaned_results = cleaned_results[:5]

    else:

        cleaned_results = cleaned_results[:5]

    print(
        "Tavily validated results:",
        len(cleaned_results)
    )

    # Remove internal score before returning
    for result in cleaned_results:

        result.pop("_score", None)

    return cleaned_results


# ============================================================
# YAHOO FINANCE
# ============================================================

def get_yahoo_data(
    company_name: Optional[str]
):

    if not company_name:

        return {}

    ticker_symbol = COMPANY_TICKERS.get(
        company_name
    )

    if not ticker_symbol:

        return {}

    try:

        ticker = yf.Ticker(
            ticker_symbol
        )

        info = ticker.info

        data = {
            "company": company_name,
            "ticker": ticker_symbol,
            "current_price": info.get(
                "currentPrice"
            ),
            "previous_close": info.get(
                "previousClose"
            ),
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
            "sector": info.get(
                "sector"
            ),
            "industry": info.get(
                "industry"
            ),
            "retrieved_at": datetime.now().isoformat(),
        }

        print(
            "Yahoo Finance data retrieved."
        )

        return data

    except Exception as e:

        print(
            "Yahoo Finance error:",
            e
        )

        return {}


# ============================================================
# GROQ USAGE
# ============================================================

def get_groq_usage():

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if not os.path.exists(
        GROQ_USAGE_FILE
    ):

        return {
            "date": today,
            "count": 0
        }

    try:

        with open(
            GROQ_USAGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            usage = json.load(file)

    except Exception:

        return {
            "date": today,
            "count": GROQ_DAILY_LIMIT
        }

    if usage.get("date") != today:

        return {
            "date": today,
            "count": 0
        }

    return {
        "date": today,
        "count": int(
            usage.get("count", 0)
        )
    }


def increment_groq_usage():

    usage = get_groq_usage()

    usage["count"] += 1

    with open(
        GROQ_USAGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            usage,
            file,
            indent=2
        )

    return usage


# ============================================================
# GEMINI
# ============================================================

def get_gemini():

    return ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    )


# ============================================================
# GROQ
# ============================================================

def get_groq():

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=GROQ_API_KEY
    )


# ============================================================
# GROQ FALLBACK
# ============================================================

def call_groq(prompt: str):

    usage = get_groq_usage()

    print(
        f"Groq backup available: "
        f"{usage['count']}/{GROQ_DAILY_LIMIT}"
    )

    if usage["count"] >= GROQ_DAILY_LIMIT:

        print(
            "Groq daily application limit reached."
        )

        return None

    try:

        model = get_groq()

        response = model.invoke(
            prompt
        )

        # Count ONLY successful request
        usage = increment_groq_usage()

        print(
            f"Groq successful request: "
            f"{usage['count']}/{GROQ_DAILY_LIMIT}"
        )

        return response.content

    except Exception as e:

        print(
            "Groq error:",
            e
        )

        return None


# ============================================================
# FORMAT WEB SOURCES FOR PROMPT
# ============================================================

def format_web_sources(
    web_results
):

    if not web_results:

        return "No web sources found."

    output = []

    for index, result in enumerate(
        web_results,
        start=1
    ):

        output.append(
            f"""
SOURCE {index}
Title: {result.get('source')}
Published: {result.get('published_date')}
URL: {result.get('url')}

Content:
{result.get('content', '')}
"""
        )

    return "\n".join(output)


# ============================================================
# FINANCE Q&A
# ============================================================

def finance_qa_agent(
    question: str
):

    company_name = detect_company(
        question
    )

    latest_news = is_latest_news_question(
        question
    )

    # ========================================================
    # RAG
    # ========================================================

    rag_results = search_knowledge_base(
        question,
        company_name=company_name,
        k=4
    )

    print(
        "RAG results:",
        len(rag_results)
    )

    # ========================================================
    # WEB
    # ========================================================

    web_results = search_web(
        question,
        company_name=company_name,
        latest_news=latest_news
    )

    # ========================================================
    # YAHOO
    # ========================================================

    yahoo_data = get_yahoo_data(
        company_name
    )

    # ========================================================
    # DATE INFORMATION
    # ========================================================

    current_date = datetime.now().strftime(
        "%d %B %Y"
    )

    # Find newest web result
    newest_web_date = None

    for result in web_results:

        result_date = parse_result_date(
            result
        )

        if result_date:

            if (
                newest_web_date is None
                or result_date > newest_web_date
            ):

                newest_web_date = result_date

    if newest_web_date:

        newest_web_date_text = (
            newest_web_date.strftime(
                "%d %B %Y"
            )
        )

    else:

        newest_web_date_text = (
            "No reliable publication date found"
        )

    # ========================================================
    # RAG CONTEXT
    # ========================================================

    rag_context = ""

    for result in rag_results:

        rag_context += (
            f"\nSOURCE: "
            f"{result.get('source')}\n"
            f"PAGE: "
            f"{result.get('page')}\n"
            f"{result.get('content')}\n"
        )

    if not rag_context:

        rag_context = (
            "No relevant company-specific "
            "RAG documents were found."
        )

    # ========================================================
    # YAHOO CONTEXT
    # ========================================================

    yahoo_context = json.dumps(
        yahoo_data,
        indent=2,
        default=str
    )

    # ========================================================
    # WEB CONTEXT
    # ========================================================

    web_context = format_web_sources(
        web_results
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a financial research assistant.

CURRENT DATE:
{current_date}

USER QUESTION:
{question}

DETECTED COMPANY:
{company_name or "None"}

LATEST NEWS QUESTION:
{latest_news}

NEWEST WEB PUBLICATION DATE FOUND:
{newest_web_date_text}


============================================================
IMPORTANT SOURCE RULES
============================================================

1. Answer only from the supplied evidence.

2. Do not invent facts, dates, financial figures,
   announcements or company developments.

3. If the supplied sources do not contain enough
   information, explicitly say that the information
   could not be verified.

4. Do NOT confuse different companies with similar names.

5. For Reliance Industries specifically, do NOT confuse it
   with:
   - Reliance Steel & Aluminum
   - Reliance Worldwide Corporation
   - Reliance Global Group
   - Reliance Infrastructure
   - Reliance Power
   - Reliance Naval

6. Preserve financial figures exactly as supplied.

7. Never convert units incorrectly.

For example:

₹95,754 crore

must remain:

₹95,754 crore

Do NOT write:

₹95 trillion

unless the source explicitly gives that number.


============================================================
LATEST NEWS RULES
============================================================

If this is a latest/recent/current news question:

1. Prioritize the newest dated source.

2. Clearly state the date of the newest source found.

3. Do NOT claim that something is the absolute latest
   news unless the evidence supports that claim.

4. Use wording such as:

"Latest verified result found in the supplied
search results was published on 16 September 2026."

instead of:

"This is the latest news as of 16 September 2026."

5. If the newest available source is old, say so.

6. Do not present old background articles as recent
   developments.

7. Do not use publication dates from unrelated companies.

8. Separate:
   - recent developments
   - older background information
   - current Yahoo Finance market data


============================================================
RAG CONTEXT
============================================================

{rag_context}


============================================================
WEB SOURCES
============================================================

{web_context}


============================================================
YAHOO FINANCE
============================================================

{yahoo_context}


============================================================
ANSWER FORMAT
============================================================

For a latest-news question, use:

## Latest verified developments

- Development
  - Date:
  - Source:

- Development
  - Date:
  - Source:

Then:

## Data currency

State the newest publication date found in the
supplied sources.

Clearly explain that the result reflects the
retrieved sources and does not prove that no
other newer article exists.

For a general finance question, give a clear,
beginner-friendly explanation.

Do not provide personalized investment advice.

Do not tell the user to buy, sell or hold a security.
"""

    # ========================================================
    # GEMINI FIRST
    # ========================================================

    provider = "Gemini"

    try:

        model = get_gemini()

        response = model.invoke(
            prompt
        )

        answer = response.content

    except Exception as e:

        print(
            "Gemini error:",
            e
        )

        error_text = str(e).lower()

        if (
            "429" in error_text
            or "quota" in error_text
            or "resource_exhausted" in error_text
            or "rate limit" in error_text
        ):

            print(
                "Gemini quota/rate limit detected."
            )

            provider = "Groq"

            answer = call_groq(
                prompt
            )

            if answer is None:

                answer = (
                    "Gemini has reached its API quota "
                    "and the Groq backup is currently "
                    "unavailable."
                )

        else:

            answer = (
                "The AI response could not be generated "
                "because of an unexpected model error."
            )

    # ========================================================
    # SOURCE OUTPUT
    # ========================================================

    sources = []

    for result in web_results:

        sources.append({
            "type": "Web",
            "source": result.get(
                "source"
            ),
            "page": None,
            "url": result.get(
                "url"
            ),
            "published_date": result.get(
                "published_date"
            ),
        })

    if yahoo_data:

        sources.append({
            "type": "Yahoo Finance",
            "source": (
                f"{yahoo_data.get('ticker')} "
                "market-data snapshot"
            ),
            "page": None,
            "url": (
                "https://finance.yahoo.com/quote/"
                f"{yahoo_data.get('ticker')}"
            ),
            "retrieved_at": yahoo_data.get(
                "retrieved_at"
            ),
        })

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "answer": answer,
        "provider": provider,
        "company": company_name,
        "retrieval": {
            "rag": len(rag_results),
            "web": len(web_results),
            "yahoo_finance": (
                1 if yahoo_data else 0
            ),
        },
        "sources": sources,
        "groq_usage": get_groq_usage(),
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    question = input(
        "Enter finance question: "
    )

    result = finance_qa_agent(
        question
    )

    print("\n")
    print("=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(result["answer"])

    print("\n")
    print("=" * 70)
    print("PROVIDER")
    print("=" * 70)
    print(result["provider"])

    print("\n")
    print("=" * 70)
    print("COMPANY")
    print("=" * 70)
    print(result["company"])

    print("\n")
    print("=" * 70)
    print("RETRIEVAL")
    print("=" * 70)
    print(result["retrieval"])

    print("\n")
    print("=" * 70)
    print("GROQ USAGE")
    print("=" * 70)

    usage = result["groq_usage"]

    print(
        f"Date: {usage['date']}"
    )

    print(
        f"Used: {usage['count']}/{GROQ_DAILY_LIMIT}"
    )

    print(
        f"Remaining: "
        f"{max(0, GROQ_DAILY_LIMIT - usage['count'])}"
    )

    print("\n")
    print("=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print(source)