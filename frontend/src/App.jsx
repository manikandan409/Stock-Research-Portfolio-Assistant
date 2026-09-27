import { useEffect, useState } from "react";
import axios from "axios";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";

import FinanceQAPage from "./FinanceQAPage";

const API_URL = "http://127.0.0.1:8000/api";

function App() {

  // ==========================================
  // PAGE NAVIGATION
  // ==========================================

  const [activePage, setActivePage] = useState("research");


  // ==========================================
  // STOCK RESEARCH STATE
  // ==========================================

  const [symbol, setSymbol] = useState("TCS.NS");

  const [loading, setLoading] = useState(false);

  const [report, setReport] = useState(null);

  const [history, setHistory] = useState([]);

  const [error, setError] = useState("");

  const [portfolioSymbols, setPortfolioSymbols] = useState(
    "TCS.NS, INFY.NS, RELIANCE.NS"
  );

  const [portfolioWeights, setPortfolioWeights] = useState(
    "40, 30, 30"
  );


  // ==========================================
  // PRICE CHART STATE
  // ==========================================

  const [priceHistory, setPriceHistory] = useState([]);

  const [pricePeriod, setPricePeriod] = useState("1mo");

  const [priceLoading, setPriceLoading] = useState(false);

  const [priceError, setPriceError] = useState("");


  // ==========================================
  // COMPANY COMPARISON STATE
  // ==========================================

  const [compareSymbol1, setCompareSymbol1] =
    useState("TCS.NS");

  const [compareSymbol2, setCompareSymbol2] =
    useState("INFY.NS");

  const [comparison, setComparison] =
    useState(null);

  const [compareLoading, setCompareLoading] =
    useState(false);

  const [compareError, setCompareError] =
    useState("");


  // ==========================================
  // LOAD RESEARCH HISTORY
  // ==========================================

  const loadHistory = async () => {

    try {

      const response = await axios.get(
        `${API_URL}/history`
      );

      setHistory(
        response.data.history || []
      );

    } catch (err) {

      console.error(
        "History error:",
        err
      );

    }

  };


  useEffect(() => {

    loadHistory();

  }, []);


  // ==========================================
  // LOAD PRICE HISTORY
  // ==========================================

  const loadPriceHistory = async (
    selectedSymbol = symbol,
    selectedPeriod = pricePeriod
  ) => {

    if (!selectedSymbol.trim()) {
      return;
    }

    setPriceLoading(true);
    setPriceError("");

    try {

      const response = await axios.get(
        `${API_URL}/price-history`,
        {
          params: {
            symbol:
              selectedSymbol
                .trim()
                .toUpperCase(),

            period: selectedPeriod,
          },
        }
      );

      const historicalData =
        response.data?.data?.historical_prices || [];

      if (historicalData.length === 0) {

        setPriceHistory([]);

        setPriceError(
          "No historical price data was found."
        );

        return;
      }

      setPriceHistory(
        historicalData
      );

    } catch (err) {

      console.error(
        "Price history error:",
        err
      );

      if (err.response?.data?.detail) {

        setPriceError(
          err.response.data.detail
        );

      } else {

        setPriceError(
          "Unable to load historical price data."
        );

      }

      setPriceHistory([]);

    } finally {

      setPriceLoading(false);

    }

  };


  // ==========================================
  // LOAD DEFAULT PRICE CHART
  // ==========================================

  useEffect(() => {

    loadPriceHistory(
      "TCS.NS",
      "1mo"
    );

  }, []);


  // ==========================================
  // RUN STOCK RESEARCH
  // ==========================================

  const runResearch = async () => {

    setLoading(true);
    setError("");

    try {

      const cleanSymbol =
        symbol
          .trim()
          .toUpperCase();

      const symbols =
        portfolioSymbols
          .split(",")
          .map(
            (item) =>
              item
                .trim()
                .toUpperCase()
          )
          .filter(Boolean);

      const weights =
        portfolioWeights
          .split(",")
          .map(
            (item) =>
              Number(item.trim())
          )
          .filter(
            (item) =>
              !Number.isNaN(item)
          )
          .map(
            (item) =>
              item / 100
          );


      // --------------------------------------
      // Check number of symbols and weights
      // --------------------------------------

      if (
        symbols.length !==
        weights.length
      ) {

        setError(
          "Portfolio symbols and portfolio weights must have the same number of values."
        );

        setLoading(false);

        return;
      }


      // --------------------------------------
      // Check total weight
      // --------------------------------------

      const totalWeight =
        weights.reduce(
          (sum, weight) =>
            sum + weight,
          0
        );

      if (
        Math.abs(
          totalWeight - 1
        ) > 0.001
      ) {

        setError(
          "Portfolio weights must add up to 100%."
        );

        setLoading(false);

        return;
      }


      // --------------------------------------
      // Check empty stock symbol
      // --------------------------------------

      if (!cleanSymbol) {

        setError(
          "Please enter a stock symbol."
        );

        setLoading(false);

        return;
      }


      // --------------------------------------
      // Send request to FastAPI
      // --------------------------------------

      const response =
        await axios.post(
          `${API_URL}/research`,
          {
            symbol:
              cleanSymbol,

            portfolio_symbols:
              symbols,

            portfolio_weights:
              weights,
          }
        );


      setReport(
        response.data.report
      );


      // --------------------------------------
      // Load chart for researched stock
      // --------------------------------------

      await loadPriceHistory(
        cleanSymbol,
        pricePeriod
      );


      await loadHistory();

    } catch (err) {

      console.error(err);

      if (
        err.response?.data?.detail
      ) {

        setError(
          err.response.data.detail
        );

      } else {

        setError(
          "Unable to connect to the FastAPI backend. Make sure FastAPI is running."
        );

      }

    }

    setLoading(false);

  };


  // ==========================================
  // CHANGE PRICE PERIOD
  // ==========================================

  const changePricePeriod =
    async (period) => {

      setPricePeriod(period);

      await loadPriceHistory(
        symbol,
        period
      );

    };


  // ==========================================
  // COMPANY COMPARISON
  // ==========================================

  const runComparison =
    async () => {

      setCompareLoading(true);
      setCompareError("");
      setComparison(null);

      try {

        const symbol1 =
          compareSymbol1
            .trim()
            .toUpperCase();

        const symbol2 =
          compareSymbol2
            .trim()
            .toUpperCase();


        // --------------------------------------
        // Validate symbols
        // --------------------------------------

        if (
          !symbol1 ||
          !symbol2
        ) {

          setCompareError(
            "Please enter both company symbols."
          );

          setCompareLoading(false);

          return;
        }


        // --------------------------------------
        // Prevent same company
        // --------------------------------------

        if (
          symbol1 === symbol2
        ) {

          setCompareError(
            "Please enter two different companies."
          );

          setCompareLoading(false);

          return;
        }


        // --------------------------------------
        // Call comparison API
        // --------------------------------------

        const response =
          await axios.get(
            `${API_URL}/compare`,
            {
              params: {
                symbol1,
                symbol2,
              },
            }
          );


        setComparison(
          response.data?.comparison ||
            null
        );

      } catch (err) {

        console.error(
          "Comparison error:",
          err
        );

        if (
          err.response?.data?.detail
        ) {

          setCompareError(
            err.response.data.detail
          );

        } else {

          setCompareError(
            "Unable to compare the companies."
          );

        }

      } finally {

        setCompareLoading(false);

      }

    };


  // ==========================================
  // PORTFOLIO CHART DATA
  // ==========================================

  const portfolioChartData =
    report?.portfolio
      ? report.portfolio.symbols.map(
          (stock, index) => ({
            name: stock,

            value:
              Number(
                report
                  .portfolio
                  .weights?.[index] ||
                  0
              ) * 100,
          })
        )
      : [];


  // ==========================================
  // GET PORTFOLIO RISK ANALYSIS
  // ==========================================

  const riskAnalysis =
    report?.portfolio_risk
      ?.analysis
      ?.analysis ||
    report?.portfolio_risk
      ?.analysis ||
    {};


  // ==========================================
  // FORMAT VALUES
  // ==========================================

  const formatValue =
    (value) => {

      if (
        value === null ||
        value === undefined
      ) {

        return "N/A";
      }

      if (
        typeof value ===
        "number"
      ) {

        return value.toLocaleString(
          undefined,
          {
            maximumFractionDigits: 2,
          }
        );

      }

      return value;

    };


  // ==========================================
  // FORMAT PERCENTAGE
  // ==========================================

  const formatPercentage =
    (value) => {

      if (
        value === null ||
        value === undefined ||
        Number.isNaN(
          Number(value)
        )
      ) {

        return "N/A";
      }

      const number =
        Number(value);

      return `${number.toFixed(2)}%`;

    };


  // ==========================================
  // SENTIMENT COLOR
  // ==========================================

  const getSentimentClass =
    (sentiment) => {

      const value =
        String(
          sentiment || ""
        ).toLowerCase();

      if (
        value === "positive"
      ) {

        return "border-green-800 bg-green-950 text-green-300";
      }

      if (
        value === "negative"
      ) {

        return "border-red-800 bg-red-950 text-red-300";
      }

      if (
        value === "mixed"
      ) {

        return "border-yellow-800 bg-yellow-950 text-yellow-300";
      }

      return "border-slate-700 bg-slate-800 text-slate-300";

    };


  // ==========================================
  // PRICE CHART DATA
  // ==========================================

  const priceChartData =
    priceHistory.map(
      (item) => ({

        date: item.date,

        close:
          Number(item.close),

        open:
          Number(item.open),

        high:
          Number(item.high),

        low:
          Number(item.low),

        volume:
          Number(item.volume),

      })
    );


  // ==========================================
  // UI
  // ==========================================

  return (

    <div className="min-h-screen bg-slate-950 text-white">


      {/* ======================================
          HEADER
      ====================================== */}

      <header className="border-b border-slate-800 bg-slate-900">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">

          <div>

            <h1 className="text-2xl font-bold">
              Stock Research Assistant
            </h1>

            <p className="mt-1 text-sm text-slate-400">
              AI-powered stock research and portfolio analysis
            </p>

          </div>

          <div className="rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300">
            AI Research System
          </div>

        </div>

      </header>


      {/* ======================================
          MAIN
      ====================================== */}

      <main className="mx-auto max-w-7xl px-6 py-8">


        {/* ======================================
            NAVIGATION
        ====================================== */}

        <div className="mb-8 flex flex-wrap gap-3">

          <button
            onClick={() =>
              setActivePage(
                "research"
              )
            }
            className={`rounded-xl px-6 py-3 font-semibold transition ${
              activePage ===
              "research"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            📊 Stock Research
          </button>


          <button
            onClick={() =>
              setActivePage(
                "finance"
              )
            }
            className={`rounded-xl px-6 py-3 font-semibold transition ${
              activePage ===
              "finance"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            🤖 Ask Anything
          </button>

        </div>


        {/* ======================================
            FINANCE Q&A PAGE
        ====================================== */}

        {activePage ===
          "finance" && (

          <FinanceQAPage />

        )}


        {/* ======================================
            STOCK RESEARCH PAGE
        ====================================== */}

        {activePage ===
          "research" && (

          <>


            {/* ====================================
                SEARCH PANEL
            ==================================== */}

            <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <h2 className="text-xl font-semibold">
                Research a Stock
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Enter a Yahoo Finance symbol to generate a complete
                research report.
              </p>


              <div className="mt-6 grid gap-5 md:grid-cols-3">


                {/* STOCK SYMBOL */}

                <div>

                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Stock Symbol
                  </label>

                  <input
                    value={symbol}
                    onChange={(e) =>
                      setSymbol(
                        e.target.value
                      )
                    }
                    placeholder="Example: TCS.NS"
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
                  />

                </div>


                {/* PORTFOLIO */}

                <div>

                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Portfolio Symbols
                  </label>

                  <input
                    value={
                      portfolioSymbols
                    }
                    onChange={(e) =>
                      setPortfolioSymbols(
                        e.target.value
                      )
                    }
                    placeholder="TCS.NS, INFY.NS, RELIANCE.NS"
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
                  />

                </div>


                {/* WEIGHTS */}

                <div>

                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Portfolio Weights (%)
                  </label>

                  <input
                    value={
                      portfolioWeights
                    }
                    onChange={(e) =>
                      setPortfolioWeights(
                        e.target.value
                      )
                    }
                    placeholder="40, 30, 30"
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
                  />

                </div>

              </div>


              {/* BUTTON */}

              <button
                onClick={
                  runResearch
                }
                disabled={loading}
                className="mt-6 rounded-lg bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {loading
                  ? "Running AI Research..."
                  : "Generate Research Report"}

              </button>


              {/* ERROR */}

              {error && (

                <div className="mt-4 rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">
                  {error}
                </div>

              )}

            </section>


            {/* ====================================
                PRICE CHART
            ==================================== */}

            <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

                <div>

                  <h3 className="text-lg font-semibold">
                    📈 Price History
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">

                    Historical closing prices for{" "}

                    <span className="font-semibold text-slate-300">

                      {symbol.toUpperCase()}

                    </span>

                  </p>

                </div>


                {/* PERIOD BUTTONS */}

                <div className="flex flex-wrap gap-2">

                  {[
                    "5d",
                    "1mo",
                    "3mo",
                    "6mo",
                    "1y",
                    "2y",
                    "5y",
                  ].map(
                    (period) => (

                      <button
                        key={period}
                        onClick={() =>
                          changePricePeriod(
                            period
                          )
                        }
                        disabled={
                          priceLoading
                        }
                        className={`rounded-lg px-3 py-2 text-xs font-semibold transition ${
                          pricePeriod ===
                          period
                            ? "bg-blue-600 text-white"
                            : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                        }`}
                      >

                        {period}

                      </button>

                    )
                  )}

                </div>

              </div>


              {/* PRICE ERROR */}

              {priceError && (

                <div className="mt-5 rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">

                  {priceError}

                </div>

              )}


              {/* LOADING */}

              {priceLoading && (

                <div className="flex h-80 items-center justify-center text-slate-400">

                  Loading price data...

                </div>

              )}


              {/* CHART */}

              {!priceLoading &&
                !priceError &&
                priceChartData.length >
                  0 && (

                  <div className="mt-6 h-96 w-full">

                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >

                      <LineChart
                        data={
                          priceChartData
                        }
                        margin={{
                          top: 10,
                          right: 20,
                          left: 10,
                          bottom: 10,
                        }}
                      >

                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="#334155"
                        />

                        <XAxis
                          dataKey="date"
                          tick={{
                            fill: "#94a3b8",
                            fontSize: 11,
                          }}
                          tickFormatter={(
                            value
                          ) => {

                            const date =
                              new Date(
                                value
                              );

                            return date.toLocaleDateString(
                              undefined,
                              {
                                month:
                                  "short",
                                day:
                                  "numeric",
                              }
                            );

                          }}
                        />

                        <YAxis
                          domain={[
                            "auto",
                            "auto",
                          ]}
                          tick={{
                            fill: "#94a3b8",
                            fontSize: 11,
                          }}
                          tickFormatter={(
                            value
                          ) =>
                            `₹${value.toLocaleString()}`
                          }
                        />

                        <Tooltip
                          contentStyle={{
                            backgroundColor:
                              "#0f172a",
                            border:
                              "1px solid #334155",
                            borderRadius:
                              "8px",
                            color:
                              "#fff",
                          }}
                          labelStyle={{
                            color:
                              "#cbd5e1",
                          }}
                          formatter={(
                            value,
                            name
                          ) => [
                            `₹${Number(
                              value
                            ).toFixed(
                              2
                            )}`,

                            name ===
                            "close"
                              ? "Close"
                              : name,

                          ]}
                        />

                        <Line
                          type="monotone"
                          dataKey="close"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={false}
                          activeDot={{
                            r: 5,
                          }}
                        />

                      </LineChart>

                    </ResponsiveContainer>

                  </div>

                )}


              {/* CHART INFORMATION */}

              {!priceLoading &&
                !priceError &&
                priceChartData.length >
                  0 && (

                  <div className="mt-5 grid gap-4 sm:grid-cols-3">

                    <InfoCard
                      title="Latest Close"
                      value={`₹${
                        priceChartData[
                          priceChartData.length -
                            1
                        ].close.toFixed(
                          2
                        )
                      }`}
                    />

                    <InfoCard
                      title="Period Start"
                      value={`₹${
                        priceChartData[
                          0
                        ].close.toFixed(
                          2
                        )
                      }`}
                    />

                    <InfoCard
                      title="Trading Sessions"
                      value={
                        priceChartData.length
                      }
                    />

                  </div>

                )}

            </section>


            {/* ====================================
                COMPANY COMPARISON
            ==================================== */}

            <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div>

                <h3 className="text-xl font-semibold">
                  🏢 Company Comparison
                </h3>

                <p className="mt-1 text-sm text-slate-400">
                  Compare fundamental and market metrics
                  between two companies.
                </p>

              </div>


              {/* COMPANY INPUTS */}

              <div className="mt-6 grid gap-5 md:grid-cols-2">


                {/* COMPANY 1 */}

                <div>

                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Company 1
                  </label>

                  <input
                    value={
                      compareSymbol1
                    }
                    onChange={(e) =>
                      setCompareSymbol1(
                        e.target.value
                      )
                    }
                    placeholder="Example: TCS.NS"
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
                  />

                </div>


                {/* COMPANY 2 */}

                <div>

                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Company 2
                  </label>

                  <input
                    value={
                      compareSymbol2
                    }
                    onChange={(e) =>
                      setCompareSymbol2(
                        e.target.value
                      )
                    }
                    placeholder="Example: INFY.NS"
                    className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 outline-none focus:border-blue-500"
                  />

                </div>

              </div>


              {/* COMPARE BUTTON */}

              <button
                onClick={
                  runComparison
                }
                disabled={
                  compareLoading
                }
                className="mt-5 rounded-lg bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {compareLoading
                  ? "Comparing..."
                  : "Compare Companies"}

              </button>


              {/* COMPARISON ERROR */}

              {compareError && (

                <div className="mt-4 rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">

                  {compareError}

                </div>

              )}


              {/* COMPARISON TABLE */}

              {comparison && (

                <div className="mt-8 overflow-x-auto">

                  <table className="w-full min-w-[700px] text-left text-sm">

                    <thead>

                      <tr className="border-b border-slate-700">

                        <th className="px-4 py-4 text-slate-400">
                          Metric
                        </th>

                        <th className="px-4 py-4 text-blue-400">
                          {compareSymbol1.toUpperCase()}
                        </th>

                        <th className="px-4 py-4 text-blue-400">
                          {compareSymbol2.toUpperCase()}
                        </th>

                      </tr>

                    </thead>


                    <tbody>


                      {/* COMPANY NAME */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 font-medium text-slate-300">
                          Company
                        </td>

                        <td className="px-4 py-4 text-slate-200">
                          {comparison
                            .company_name?.[
                              compareSymbol1.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                        <td className="px-4 py-4 text-slate-200">
                          {comparison
                            .company_name?.[
                              compareSymbol2.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                      </tr>


                      {/* SECTOR */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Sector
                        </td>

                        <td className="px-4 py-4">
                          {comparison
                            .sector?.[
                              compareSymbol1.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                        <td className="px-4 py-4">
                          {comparison
                            .sector?.[
                              compareSymbol2.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                      </tr>


                      {/* INDUSTRY */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Industry
                        </td>

                        <td className="px-4 py-4">
                          {comparison
                            .industry?.[
                              compareSymbol1.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                        <td className="px-4 py-4">
                          {comparison
                            .industry?.[
                              compareSymbol2.toUpperCase()
                            ] ||
                            "N/A"}
                        </td>

                      </tr>


                      {/* LATEST PRICE */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Latest Price
                        </td>

                        <td className="px-4 py-4 font-semibold">
                          ₹
                          {formatValue(
                            comparison
                              .close?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4 font-semibold">
                          ₹
                          {formatValue(
                            comparison
                              .close?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* MARKET CAP */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Market Cap
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .market_cap?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .market_cap?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* P/E */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          P/E Ratio
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .pe_ratio?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .pe_ratio?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* FORWARD P/E */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Forward P/E
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .forward_pe?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .forward_pe?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* P/B */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Price / Book
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .price_to_book?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .price_to_book?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* PROFIT MARGIN */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Profit Margin
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .profit_margin?.[
                                  compareSymbol1.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .profit_margin?.[
                                  compareSymbol2.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                      </tr>


                      {/* REVENUE GROWTH */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Revenue Growth
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .revenue_growth?.[
                                  compareSymbol1.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .revenue_growth?.[
                                  compareSymbol2.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                      </tr>


                      {/* ROE */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Return on Equity
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .return_on_equity?.[
                                  compareSymbol1.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            Number(
                              comparison
                                .return_on_equity?.[
                                  compareSymbol2.toUpperCase()
                                ]
                            ) * 100
                          )}
                        </td>

                      </tr>


                      {/* DEBT / EQUITY */}

                      <tr className="border-b border-slate-800">

                        <td className="px-4 py-4 text-slate-400">
                          Debt / Equity
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .debt_to_equity?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatValue(
                            comparison
                              .debt_to_equity?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>


                      {/* DIVIDEND YIELD */}

                      <tr>

                        <td className="px-4 py-4 text-slate-400">
                          Dividend Yield
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            comparison
                              .dividend_yield?.[
                                compareSymbol1.toUpperCase()
                              ]
                          )}
                        </td>

                        <td className="px-4 py-4">
                          {formatPercentage(
                            comparison
                              .dividend_yield?.[
                                compareSymbol2.toUpperCase()
                              ]
                          )}
                        </td>

                      </tr>

                    </tbody>

                  </table>

                </div>

              )}

            </section>


            {/* ====================================
                REPORT
            ==================================== */}

            {report && (

              <div className="mt-8 space-y-6">


                {/* REPORT HEADER */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

                    <div>

                      <p className="text-sm text-blue-400">
                        AI RESEARCH REPORT
                      </p>

                      <h2 className="mt-1 text-2xl font-bold">
                        {report.report_title}
                      </h2>

                      <p className="mt-2 text-sm text-slate-400">

                        Generated:{" "}

                        {report.report_generated_date ||
                          "N/A"}

                      </p>

                    </div>


                    <div className="rounded-xl bg-slate-800 px-5 py-4">

                      <p className="text-xs text-slate-400">
                        Stock
                      </p>

                      <p className="text-xl font-bold">
                        {report.company}
                      </p>

                    </div>

                  </div>

                </section>


                {/* MARKET SNAPSHOT */}

                {report.market_snapshot && (

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h3 className="text-lg font-semibold">
                      Market Snapshot
                    </h3>

                    <p className="mt-1 text-sm text-slate-400">
                      Latest available market data
                    </p>


                    <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

                      <InfoCard
                        title="Latest Price"
                        value={formatValue(
                          report
                            .market_snapshot
                            .close
                        )}
                      />

                      <InfoCard
                        title="Open"
                        value={formatValue(
                          report
                            .market_snapshot
                            .open
                        )}
                      />

                      <InfoCard
                        title="Day High"
                        value={formatValue(
                          report
                            .market_snapshot
                            .high
                        )}
                      />

                      <InfoCard
                        title="Day Low"
                        value={formatValue(
                          report
                            .market_snapshot
                            .low
                        )}
                      />

                      <InfoCard
                        title="Volume"
                        value={formatValue(
                          report
                            .market_snapshot
                            .volume
                        )}
                      />

                    </div>


                    <p className="mt-4 text-xs text-slate-500">

                      Market data date:{" "}

                      {report
                        .market_snapshot
                        .date ||
                        "N/A"}

                    </p>

                  </section>

                )}


                {/* BUSINESS OVERVIEW */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Business Overview
                  </h3>


                  <div className="mt-5 grid gap-4 md:grid-cols-3">

                    <InfoCard
                      title="Company"
                      value={
                        report
                          .business_overview
                          ?.company_name
                      }
                    />

                    <InfoCard
                      title="Sector"
                      value={
                        report
                          .business_overview
                          ?.sector
                      }
                    />

                    <InfoCard
                      title="Industry"
                      value={
                        report
                          .business_overview
                          ?.industry
                      }
                    />

                  </div>

                </section>


                {/* FINANCIAL FUNDAMENTALS */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Financial Fundamentals
                  </h3>


                  <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                    {Object.entries(
                      report
                        .financial_fundamentals ||
                        {}
                    ).map(
                      ([key, value]) => (

                        <InfoCard
                          key={key}
                          title={formatTitle(
                            key
                          )}
                          value={formatValue(
                            value
                          )}
                        />

                      )
                    )}

                  </div>

                </section>


                {/* ANNUAL REPORT / RAG */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Annual Report Research
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">
                    Information retrieved from the project's
                    RAG knowledge base.
                  </p>


                  <div className="mt-5 space-y-4">

                    {report
                      .annual_report_research
                      ?.length > 0 ? (

                      report
                        .annual_report_research
                        .map(
                          (
                            item,
                            index
                          ) => (

                            <div
                              key={
                                index
                              }
                              className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                            >

                              <div className="flex flex-wrap gap-3 text-xs text-slate-400">

                                <span>

                                  Source:{" "}

                                  {item.source ||
                                    "Unknown"}

                                </span>

                                <span>

                                  Page:{" "}

                                  {item.page ??
                                    "N/A"}

                                </span>

                              </div>


                              <p className="mt-3 text-sm leading-7 text-slate-300">

                                {item.content}

                              </p>

                            </div>

                          )
                        )

                    ) : (

                      <p className="text-slate-400">

                        No company-specific annual report information
                        was retrieved from the RAG knowledge base.

                      </p>

                    )}

                  </div>

                </section>


                {/* NEWS & SENTIMENT */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">

                    <div>

                      <h3 className="text-lg font-semibold">
                        Recent News & Sentiment
                      </h3>

                      <p className="mt-1 text-sm text-slate-400">
                        Recent news retrieved through Tavily.
                      </p>

                    </div>


                    <div
                      className={`rounded-lg border px-4 py-2 text-sm font-semibold ${getSentimentClass(
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.overall_sentiment
                      )}`}
                    >

                      Overall:{" "}

                      {report
                        .recent_news
                        ?.sentiment_summary
                        ?.overall_sentiment ||
                        "N/A"}

                    </div>

                  </div>


                  {/* SENTIMENT SUMMARY */}

                  <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

                    <InfoCard
                      title="Articles"
                      value={
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.articles_analyzed ??
                        "N/A"
                      }
                    />

                    <InfoCard
                      title="Positive"
                      value={
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.positive_articles ??
                        0
                      }
                    />

                    <InfoCard
                      title="Negative"
                      value={
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.negative_articles ??
                        0
                      }
                    />

                    <InfoCard
                      title="Mixed"
                      value={
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.mixed_articles ??
                        0
                      }
                    />

                    <InfoCard
                      title="Neutral"
                      value={
                        report
                          .recent_news
                          ?.sentiment_summary
                          ?.neutral_articles ??
                        0
                      }
                    />

                  </div>


                  {/* NEWS ARTICLES */}

                  <div className="mt-6 space-y-4">

                    {report
                      .recent_news
                      ?.news_articles
                      ?.length > 0 ? (

                      report
                        .recent_news
                        .news_articles
                        .map(
                          (
                            article,
                            index
                          ) => (

                            <div
                              key={
                                index
                              }
                              className="rounded-xl border border-slate-800 bg-slate-950 p-5"
                            >

                              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">

                                <div className="flex-1">

                                  <h4 className="font-semibold text-slate-200">

                                    {article.title ||
                                      "Untitled article"}

                                  </h4>


                                  <p className="mt-2 text-xs text-slate-500">

                                    {article.published_date ||
                                      "Date unavailable"}

                                  </p>

                                </div>


                                <span
                                  className={`w-fit rounded-lg border px-3 py-1 text-xs font-semibold ${getSentimentClass(
                                    article.sentiment
                                  )}`}
                                >

                                  {article.sentiment ||
                                    "neutral"}

                                </span>

                              </div>


                              {/* EVIDENCE */}

                              {article.evidence && (

                                <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900 p-4">

                                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">

                                    Evidence / Signals

                                  </p>

                                  <p className="mt-2 text-sm leading-6 text-slate-300">

                                    {article.evidence}

                                  </p>

                                </div>

                              )}


                              {/* SIGNAL COUNTS */}

                              <div className="mt-4 flex flex-wrap gap-3 text-xs">

                                <span className="rounded-lg bg-slate-800 px-3 py-2 text-slate-300">

                                  Positive signals:{" "}

                                  {article
                                    .positive_signal_count ??
                                    0}

                                </span>


                                <span className="rounded-lg bg-slate-800 px-3 py-2 text-slate-300">

                                  Negative signals:{" "}

                                  {article
                                    .negative_signal_count ??
                                    0}

                                </span>

                              </div>


                              {/* ARTICLE LINK */}

                              {article.url && (

                                <a
                                  href={
                                    article.url
                                  }
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="mt-4 inline-block text-sm text-blue-400 hover:text-blue-300"
                                >

                                  Read source →

                                </a>

                              )}

                            </div>

                          )
                        )

                    ) : (

                      <p className="text-slate-400">
                        No recent news articles available.
                      </p>

                    )}

                  </div>

                </section>


                {/* PORTFOLIO RISK */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Portfolio Risk Profile
                  </h3>

                  <p className="mt-1 text-sm text-slate-400">

                    Quantitative risk metrics calculated from the
                    selected portfolio.

                  </p>


                  <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                    <InfoCard
                      title="Annualized Return"
                      value={
                        riskAnalysis
                          .annualized_return !==
                        undefined
                          ? formatPercentage(
                              riskAnalysis
                                .annualized_return
                            )
                          : "N/A"
                      }
                    />


                    <InfoCard
                      title="Annualized Volatility"
                      value={
                        riskAnalysis
                          .annualized_volatility !==
                        undefined
                          ? formatPercentage(
                              riskAnalysis
                                .annualized_volatility
                            )
                          : "N/A"
                      }
                    />


                    <InfoCard
                      title="Portfolio Beta"
                      value={formatValue(
                        riskAnalysis
                          .portfolio_beta
                      )}
                    />


                    <InfoCard
                      title="Largest Holding"
                      value={
                        riskAnalysis
                          .concentration
                          ?.largest_holding_weight !==
                        undefined
                          ? formatPercentage(
                              riskAnalysis
                                .concentration
                                .largest_holding_weight
                            )
                          : "N/A"
                      }
                    />

                  </div>


                  {/* CONCENTRATION METRICS */}

                  <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                    <InfoCard
                      title="Concentration HHI"
                      value={formatValue(
                        riskAnalysis
                          .concentration
                          ?.hhi
                      )}
                    />


                    <InfoCard
                      title="Effective Holdings"
                      value={formatValue(
                        riskAnalysis
                          .concentration
                          ?.effective_number_of_holdings
                      )}
                    />


                    <InfoCard
                      title="Benchmark"
                      value={
                        riskAnalysis
                          .benchmark ||
                        "NIFTY 50"
                      }
                    />


                    <InfoCard
                      title="Trading Days"
                      value={formatValue(
                        riskAnalysis
                          .trading_days
                      )}
                    />

                  </div>


                  <p className="mt-5 text-xs text-slate-500">

                    Risk data period:{" "}

                    {riskAnalysis
                      .data_period ||
                      "N/A"}

                  </p>

                </section>


                {/* PORTFOLIO CHART */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Portfolio Allocation
                  </h3>


                  <div className="mt-5 grid gap-6 md:grid-cols-2">


                    {/* PIE CHART */}

                    <div className="h-72">

                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >

                        <PieChart>

                          <Pie
                            data={
                              portfolioChartData
                            }
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={90}
                            label
                          >

                            {portfolioChartData.map(
                              (
                                _,
                                index
                              ) => (

                                <Cell
                                  key={
                                    index
                                  }
                                />

                              )
                            )}

                          </Pie>

                          <Tooltip />

                        </PieChart>

                      </ResponsiveContainer>

                    </div>


                    {/* ALLOCATION TABLE */}

                    <div className="overflow-x-auto">

                      <table className="w-full text-left text-sm">

                        <thead className="border-b border-slate-800 text-slate-400">

                          <tr>

                            <th className="px-4 py-3">
                              Symbol
                            </th>

                            <th className="px-4 py-3">
                              Weight
                            </th>

                          </tr>

                        </thead>


                        <tbody>

                          {report
                            .portfolio
                            ?.symbols
                            ?.map(
                              (
                                stock,
                                index
                              ) => (

                                <tr
                                  key={`${stock}-${index}`}
                                  className="border-b border-slate-800"
                                >

                                  <td className="px-4 py-3 font-medium">
                                    {stock}
                                  </td>

                                  <td className="px-4 py-3 text-slate-300">

                                    {(
                                      Number(
                                        report
                                          .portfolio
                                          .weights?.[
                                          index
                                        ] || 0
                                      ) * 100
                                    ).toFixed(
                                      1
                                    )}

                                    %

                                  </td>

                                </tr>

                              )
                            )}

                        </tbody>

                      </table>

                    </div>

                  </div>

                </section>


                {/* OPEN QUESTIONS */}

                {report
                  .open_questions
                  ?.length > 0 && (

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h3 className="text-lg font-semibold">
                      Open Questions
                    </h3>

                    <p className="mt-1 text-sm text-slate-400">
                      Items that may require additional research.
                    </p>


                    <ul className="mt-5 space-y-3">

                      {report
                        .open_questions
                        .map(
                          (
                            question,
                            index
                          ) => (

                            <li
                              key={
                                index
                              }
                              className="rounded-lg bg-slate-950 p-4 text-sm text-slate-300"
                            >

                              • {question}

                            </li>

                          )
                        )}

                    </ul>

                  </section>

                )}


                {/* LIMITATIONS */}

                {report
                  .limitations
                  ?.length > 0 && (

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h3 className="text-lg font-semibold">
                      Limitations
                    </h3>


                    <ul className="mt-5 space-y-3">

                      {report
                        .limitations
                        .map(
                          (
                            limitation,
                            index
                          ) => (

                            <li
                              key={
                                index
                              }
                              className="rounded-lg bg-slate-950 p-4 text-sm text-slate-300"
                            >

                              • {limitation}

                            </li>

                          )
                        )}

                    </ul>

                  </section>

                )}


                {/* DATA PERIOD */}

                {report.data_period && (

                  <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                    <h3 className="text-lg font-semibold">
                      Data Period
                    </h3>


                    <div className="mt-4 space-y-2 text-sm text-slate-300">

                      <p>

                        <span className="text-slate-500">
                          Report generated:
                        </span>{" "}

                        {report
                          .data_period
                          .report_generated_date ||
                          "N/A"}

                      </p>


                      <p>

                        <span className="text-slate-500">
                          Market data:
                        </span>{" "}

                        {report
                          .data_period
                          .market_data_date ||
                          "N/A"}

                      </p>


                      <p>

                        <span className="text-slate-500">
                          Risk period:
                        </span>{" "}

                        {report
                          .data_period
                          .risk_data_period ||
                          "N/A"}

                      </p>


                      <p>

                        <span className="text-slate-500">
                          Annual report:
                        </span>{" "}

                        {report
                          .data_period
                          .annual_report_period ||
                          "N/A"}

                      </p>

                    </div>

                  </section>

                )}


                {/* DATA SOURCES */}

                <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">

                  <h3 className="text-lg font-semibold">
                    Data Sources
                  </h3>


                  <ul className="mt-4 space-y-2 text-sm text-slate-300">

                    {report
                      .data_sources
                      ?.map(
                        (
                          source,
                          index
                        ) => (

                          <li
                            key={
                              index
                            }
                          >

                            • {source}

                          </li>

                        )
                      )}

                  </ul>

                </section>


                {/* DISCLAIMER */}

                <section className="rounded-xl border border-yellow-800 bg-yellow-950 p-5">

                  <h3 className="font-semibold text-yellow-300">
                    Educational Disclaimer
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-yellow-200">

                    {report
                      .disclaimer ||
                      "This report is provided for educational and research purposes only and is not investment advice."}

                  </p>

                </section>

              </div>

            )}


            {/* ====================================
                HISTORY
            ==================================== */}

            <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">

              <div className="flex items-center justify-between">

                <div>

                  <h2 className="text-xl font-semibold">
                    Research History
                  </h2>

                  <p className="mt-1 text-sm text-slate-400">
                    Reports stored in MongoDB
                  </p>

                </div>


                <button
                  onClick={
                    loadHistory
                  }
                  className="rounded-lg bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700"
                >

                  Refresh

                </button>

              </div>


              <div className="mt-5 space-y-3">

                {history.length ===
                0 ? (

                  <p className="text-sm text-slate-400">
                    No research reports found.
                  </p>

                ) : (

                  history.map(
                    (
                      item,
                      index
                    ) => (

                      <button
                        key={
                          item._id ||
                          index
                        }
                        onClick={() =>
                          setReport(
                            item
                          )
                        }
                        className="w-full rounded-xl border border-slate-800 bg-slate-950 p-4 text-left transition hover:border-blue-600"
                      >

                        <div className="flex flex-col justify-between gap-2 md:flex-row">

                          <div>

                            <p className="font-semibold">
                              {item.report_title}
                            </p>

                            <p className="mt-1 text-sm text-slate-400">
                              {item.company}
                            </p>

                          </div>


                          <p className="text-xs text-slate-500">
                            {item.created_at}
                          </p>

                        </div>

                      </button>

                    )
                  )

                )}

              </div>

            </section>

          </>

        )}

      </main>


      {/* ======================================
          FOOTER
      ====================================== */}

      <footer className="border-t border-slate-800 bg-slate-900 py-6">

        <p className="text-center text-xs text-slate-500">

          Stock Research & Portfolio Assistant •
          Educational and research purposes only

        </p>

      </footer>

    </div>

  );

}


// ==========================================
// INFO CARD COMPONENT
// ==========================================

function InfoCard({
  title,
  value
}) {

  return (

    <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">

      <p className="text-xs uppercase tracking-wide text-slate-500">

        {title}

      </p>


      <p className="mt-2 break-words text-lg font-semibold text-slate-200">

        {value ??
          "N/A"}

      </p>

    </div>

  );

}


// ==========================================
// FORMAT OBJECT KEY
// ==========================================

function formatTitle(key) {

  return key
    .replaceAll(
      "_",
      " "
    )
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );

}


export default App;