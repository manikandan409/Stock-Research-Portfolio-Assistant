# Stock Research & Portfolio Assistant

An AI-powered **Stock Research & Portfolio Assistant** that helps users understand stocks, financial fundamentals, recent news sentiment, portfolio risk, and financial concepts through a combination of **LangGraph, RAG, MCP, Tavily, Yahoo Finance, FastAPI, React, and MongoDB**.

> **Disclaimer:** This project is for educational and research purposes only. It does not provide investment advice, buy/sell recommendations, or price targets.

---

## 🚀 Features

### 1. Stock Research

Generate a structured research report for a company including:

* Business overview
* Market snapshot
* Key financial ratios
* Revenue and profitability information
* Annual report research
* Recent news
* News sentiment
* Risk information
* Open research questions
* Data sources and limitations

### 2. Fundamental Analysis

The Fundamental Agent retrieves financial information and combines it with information from the RAG knowledge base.

Metrics include:

* Market capitalization
* P/E ratio
* Forward P/E
* Price-to-book ratio
* Profit margin
* Revenue growth
* Return on equity
* Debt-to-equity ratio
* Dividend yield

### 3. News Sentiment Analysis

The Sentiment Agent uses **Tavily** to retrieve recent financial news.

The system analyzes news articles and provides:

* Positive signals
* Negative signals
* Neutral signals
* Evidence from individual articles
* Article titles
* Publication dates
* Source URLs

### 4. Portfolio Risk Analysis

The Risk Agent analyzes portfolio allocations and calculates:

* Annualized return
* Annualized volatility
* Portfolio beta
* Concentration using HHI
* Effective number of holdings
* Largest holding weight
* Individual holding information
* Benchmark comparison

### 5. RAG Knowledge Base

The project uses **Retrieval-Augmented Generation (RAG)** to retrieve information from financial documents.

Knowledge sources include:

* Company annual reports
* SEBI investor education material
* Financial glossary

The vector database is created using **ChromaDB** and **Hugging Face sentence-transformer embeddings**.

### 6. Finance Q&A

Users can ask educational questions such as:

* What does a P/E ratio of 35 mean?
* What is beta?
* What is diversification?
* What does debt-to-equity mean?
* How should financial ratios be interpreted?

The system combines relevant financial knowledge, market information, and AI-generated explanations.

### 7. Price History

Users can view historical stock price information and visualize price movements for different time periods.

### 8. Company Comparison

Compare multiple companies using financial and market metrics.

### 9. Research History

Research requests and results can be stored using **MongoDB** for later reference.

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │     React Frontend   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ LangGraph Supervisor │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │ Fundamental  │ │  Sentiment   │ │     Risk     │
      │    Agent     │ │    Agent     │ │    Agent     │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             ▼                ▼                ▼
          Financial         Tavily           Risk
            Data             News          Calculation
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                     ┌─────────────────┐
                     │   Report Agent  │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Research Report │
                     └─────────────────┘
```

---

# 🧠 LangGraph Workflow

The Supervisor determines the type of user request and routes it to the appropriate agent.

### Conceptual Question

```text
User Question
     ↓
Supervisor
     ↓
RAG Agent
     ↓
Knowledge Base
     ↓
Educational Answer
```

### Stock Research

```text
User Query
     ↓
Supervisor
     ↓
┌───────────────┬───────────────┬───────────────┐
│ Fundamental   │   Sentiment   │      Risk     │
│    Agent      │     Agent     │     Agent     │
└───────┬───────┴───────┬───────┴───────┬───────┘
        │               │               │
        └───────────────┼───────────────┘
                        ↓
                  Report Agent
                        ↓
                 Final Research
```

The research branches can run independently and their results are aggregated before the final report is generated.

---

# 🔌 MCP Tools

The project includes an MCP server using **FastMCP**.

Available tools include:

* `stock_price`
* `company_financials`
* `portfolio_risk`

The underlying financial functionality includes:

* Stock price retrieval
* Company financial information
* Portfolio risk calculations

---

# 📚 RAG Pipeline

```text
Financial Documents
       ↓
PDF Loading
       ↓
Text Splitting
       ↓
Embeddings
       ↓
ChromaDB Vector Store
       ↓
Similarity Search
       ↓
Relevant Financial Context
       ↓
AI Response
```

### Embedding Model

```text
sentence-transformers/all-MiniLM-L6-v2
```

### Vector Database

```text
ChromaDB
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* Python
* FastAPI
* Uvicorn

## AI / LLM

* Google Gemini
* Groq fallback
* LangChain
* LangGraph

## RAG

* ChromaDB
* Hugging Face
* Sentence Transformers
* PyPDF

## Financial Data

* Yahoo Finance
* yfinance

## News

* Tavily

## Database

* MongoDB

## MCP

* Model Context Protocol
* FastMCP

---

# 📁 Project Structure

```text
Stock-Research-Portfolio-Assistant/
│
├── backend/
│   ├── agents/
│   │   ├── supervisor.py
│   │   ├── fundamental_agent.py
│   │   ├── sentiment_agent.py
│   │   ├── risk_agent.py
│   │   ├── report_agent.py
│   │   ├── rag_agent.py
│   │   └── finance_qa_agent.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── graph/
│   │   └── research_graph.py
│   │
│   ├── database.py
│   └── main.py
│
├── mcp_server/
│   ├── server.py
│   ├── price_tool.py
│   ├── financial_tool.py
│   └── risk_tool.py
│
├── rag/
│   ├── documents/
│   ├── vectorstore/
│   ├── ingest.py
│   ├── retriever.py
│   └── embeddings.py
│
├── data/
│   ├── annual_reports/
│   ├── sebi/
│   └── glossary/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/manikandan409/Stock-Research-Portfolio-Assistant.git
```

Go into the project:

```bash
cd Stock-Research-Portfolio-Assistant
```

---

## 2. Create a Python Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

---

## 3. Install Python Dependencies

If `requirements.txt` is available:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as the template.

Example:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
MONGO_URI=mongodb://localhost:27017
GROQ_DAILY_LIMIT=10
```

**Never commit your real `.env` file or API keys to GitHub.**

---

# 🗄️ MongoDB

Make sure MongoDB is running locally.

Default connection:

```text
mongodb://localhost:27017
```

The application uses MongoDB for research history and related stored information.

---

# 📖 Build the RAG Knowledge Base

Run:

```powershell
.\.venv\Scripts\python.exe rag\ingest.py
```

This processes the available financial documents and creates the local vector database.

---

# ▶️ Run the Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 💻 Run the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🧪 Example Queries

### Stock Research

```text
Research TCS
```

### Fundamentals

```text
Give me the fundamentals of Infosys
```

### News

```text
What is the recent sentiment around Tata Motors?
```

### Portfolio Risk

```text
Analyze a portfolio with 40% TCS, 30% HDFC Bank and 30% Reliance.
```

### Financial Concept

```text
What does a P/E ratio of 35 mean?
```

---

# 🛡️ Guardrails

The system is designed for educational financial research.

It does **not**:

* Provide buy recommendations
* Provide sell recommendations
* Give price targets
* Predict guaranteed returns
* Present research as personalized investment advice

Reports include:

* Data dates
* Data sources
* Limitations
* Educational disclaimer

---

# 📊 Current Application Modules

| Module                   | Status |
| ------------------------ | ------ |
| LangGraph Supervisor     | ✅      |
| Fundamental Agent        | ✅      |
| Sentiment Agent          | ✅      |
| Risk Agent               | ✅      |
| Report Agent             | ✅      |
| RAG Knowledge Base       | ✅      |
| Tavily News Search       | ✅      |
| MCP Server               | ✅      |
| Parallel Research        | ✅      |
| Conceptual RAG Questions | ✅      |
| FastAPI Backend          | ✅      |
| React Frontend           | ✅      |
| Price History            | ✅      |
| Company Comparison       | ✅      |
| Finance Q&A              | ✅      |
| MongoDB History          | ✅      |

---

# 🔮 Future Improvements

Potential future improvements include:

* More company annual reports
* More financial data sources
* Advanced NLP-based sentiment classification
* More portfolio analytics
* Additional financial indicators
* Interactive portfolio dashboards
* Improved MCP client-server integration
* More financial education resources
* Enhanced report visualization

---

# 📌 Project Information

**Project:** Stock Research & Portfolio Assistant

**Domain:** Finance

**Purpose:** AI-assisted financial research and education

**Repository:**

https://github.com/manikandan409/Stock-Research-Portfolio-Assistant

---

# ⚖️ Disclaimer

This project is developed for **educational and research purposes only**.

The information generated by this application should not be considered financial, investment, legal, tax, or professional advice. Users should independently verify financial information and consult qualified professionals before making financial decisions.
