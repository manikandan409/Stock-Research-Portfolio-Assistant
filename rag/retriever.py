from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
import os


# ============================================================
# VECTORSTORE PATH
# ============================================================

VECTORSTORE_PATH = os.path.join(
    os.path.dirname(__file__),
    "vectorstore"
)


# ============================================================
# SEARCH KNOWLEDGE BASE
# ============================================================

def search_knowledge_base(
    query: str,
    company_name: str = None,
    k: int = 4
):

    # --------------------------------------------------------
    # If vectorstore does not exist, return empty results
    # --------------------------------------------------------

    if not os.path.exists(VECTORSTORE_PATH):
        return []

    try:

        embeddings = get_embeddings()

        vectorstore = Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=embeddings
        )

        results = vectorstore.similarity_search_with_score(
            query,
            k=k * 5
        )

    except Exception as e:

        print("RAG search error:", e)

        return []


    filtered_results = []


    # ========================================================
    # FILTER RESULTS
    # ========================================================

    for document, score in results:

        source = document.metadata.get(
            "source",
            "Unknown"
        )

        content = document.page_content

        source_lower = source.lower()
        content_lower = content.lower()


        # ====================================================
        # COMPANY-SPECIFIC SEARCH
        # ====================================================

        if company_name:

            company_lower = company_name.lower()

            company_match = (
                company_lower in source_lower
                or company_lower in content_lower
            )

            if company_match:

                filtered_results.append({
                    "content": content,
                    "source": source,
                    "page": document.metadata.get(
                        "page",
                        "Unknown"
                    ),
                    "score": float(score)
                })


        # ====================================================
        # GENERAL FINANCE SEARCH
        # ====================================================

        else:

            # Only allow general documents.
            # Do NOT return another company's annual report.

            if (
                "sebi" in source_lower
                or "glossary" in source_lower
            ):

                filtered_results.append({
                    "content": content,
                    "source": source,
                    "page": document.metadata.get(
                        "page",
                        "Unknown"
                    ),
                    "score": float(score)
                })


    # ========================================================
    # IMPORTANT
    # ========================================================
    #
    # NEVER FALL BACK TO AN UNRELATED COMPANY REPORT.
    #
    # Example:
    #
    # Reliance question
    #       ↓
    # No Reliance report
    #       ↓
    # Return []
    #
    # NOT:
    #
    # No Reliance report
    #       ↓
    # Use TCS report
    #
    # ========================================================

    return filtered_results[:k]