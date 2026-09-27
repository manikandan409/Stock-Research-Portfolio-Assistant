import sys
import os

# -----------------------------------------
# Add project root to Python path
# -----------------------------------------

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from rag.retriever import search_knowledge_base


# ==================================================
# RAG AGENT
# ==================================================

def rag_agent(question: str):

    print("\n[RAG AGENT] Searching knowledge base...")

    results = search_knowledge_base(
        question,
        company_name=None,
        k=4
    )

    if not results:

        return {
            "agent": "rag_agent",
            "status": "no_results",
            "question": question,
            "results": [],
            "message": (
                "No relevant information was found "
                "in the financial knowledge base."
            )
        }

    research_results = []

    for result in results:

        research_results.append({
            "content": result.get(
                "content",
                ""
            ),
            "source": result.get(
                "source",
                "Unknown"
            ),
            "page": result.get(
                "page",
                "Unknown"
            ),
            "score": result.get(
                "score",
                None
            )
        })

    return {
        "agent": "rag_agent",
        "status": "success",
        "question": question,
        "results": research_results
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    question = "What does a P/E ratio mean?"

    result = rag_agent(question)

    print("\n===================================")
    print(" RAG AGENT")
    print("===================================")

    print("\nQuestion:")
    print(result["question"])

    print("\nStatus:")
    print(result["status"])

    print("\nResults:")

    for item in result["results"]:

        print("\n-----------------------------------")
        print("SOURCE:", item["source"])
        print("PAGE:", item["page"])
        print("-----------------------------------")
        print(item["content"][:1000])