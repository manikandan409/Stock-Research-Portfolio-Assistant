import { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api";

function FinanceQAPage() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askQuestion = async () => {

    if (!question.trim()) {
      setError("Please enter a finance question.");
      return;
    }

    try {

      setLoading(true);
      setError("");
      setAnswer("");
      setSources([]);

      const response = await axios.post(
        `${API_URL}/finance-question`,
        {
          question: question
        }
      );

      setAnswer(response.data.answer || "");
      setSources(response.data.sources || []);

    } catch (error) {

      setError(
        error.response?.data?.detail ||
        "Something went wrong."
      );

    } finally {

      setLoading(false);

    }
  };


  const exampleQuestions = [
    "What is P/E ratio?",
    "What is market capitalization?",
    "What is CAGR?",
    "What is EBITDA?",
    "What is diversification?",
    "What is the difference between stocks and bonds?"
  ];


  return (

    <div className="space-y-6">

      {/* HEADER */}

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

        <div className="mb-6">

          <div className="mb-2 text-3xl">
            🤖
          </div>

          <h1 className="text-3xl font-bold text-white">
            Ask Anything
          </h1>

          <p className="mt-2 text-slate-400">
            Ask questions about finance,
            stocks, financial concepts and
            company reports.
          </p>

        </div>


        {/* QUESTION */}

        <label className="mb-2 block text-sm font-medium text-slate-300">
          Your Question
        </label>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: What is P/E ratio?"
          rows={5}
          className="w-full resize-none rounded-xl border border-slate-700 bg-slate-950 p-4 text-white outline-none transition focus:border-blue-500"
        />


        {/* BUTTON */}

        <button
          onClick={askQuestion}
          disabled={loading}
          className="mt-4 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Thinking..." : "Ask Question"}
        </button>


        {/* ERROR */}

        {error && (

          <div className="mt-5 rounded-xl border border-red-800 bg-red-950/40 p-4 text-red-300">
            {error}
          </div>

        )}

      </section>


      {/* ANSWER */}

      {answer && (

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

          <h2 className="mb-5 text-xl font-semibold text-white">
            Answer
          </h2>

          <div className="whitespace-pre-wrap leading-8 text-slate-300">
            {answer}
          </div>

        </section>

      )}


      {/* SOURCES */}

      {sources.length > 0 && (

        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

          <h2 className="mb-5 text-xl font-semibold text-white">
            📚 Sources
          </h2>

          <div className="space-y-3">

            {sources.map((source, index) => (

              <div
                key={index}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >

                <p className="text-sm text-slate-300">
                  {source.source}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Page: {source.page ?? "N/A"}
                </p>

              </div>

            ))}

          </div>

        </section>

      )}


      {/* EXAMPLE QUESTIONS */}

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-8">

        <h2 className="mb-5 text-xl font-semibold text-white">
          Try asking
        </h2>

        <div className="grid gap-3 md:grid-cols-2">

          {exampleQuestions.map((item) => (

            <button
              key={item}
              onClick={() => setQuestion(item)}
              className="rounded-xl border border-slate-800 bg-slate-950 p-4 text-left text-slate-300 transition hover:border-blue-500 hover:text-white"
            >
              {item}
            </button>

          ))}

        </div>

      </section>


      {/* DISCLAIMER */}

      <div className="rounded-xl border border-slate-800 bg-slate-950 p-5 text-sm leading-6 text-slate-500">

        This Finance Q&A feature is intended
        for educational and research purposes
        only. It does not provide personalized
        investment advice or recommendations
        to buy or sell securities.

      </div>

    </div>

  );
}

export default FinanceQAPage;