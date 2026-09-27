import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from rag.embeddings import get_embeddings


DOCUMENT_FOLDERS = [
    "data/annual_reports",
    "data/sebi",
    "data/glossary"
]

VECTORSTORE_PATH = "rag/vectorstore"


def load_documents():

    documents = []

    for folder in DOCUMENT_FOLDERS:

        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):

            if filename.lower().endswith(".pdf"):

                file_path = os.path.join(
                    folder,
                    filename
                )

                print(f"Loading: {file_path}")

                loader = PyPDFLoader(file_path)

                documents.extend(
                    loader.load()
                )

    return documents


def create_vectorstore():

    documents = load_documents()

    if not documents:

        print("No PDF documents found.")
        print("Add PDFs to the data folders first.")
        return

    print(
        f"Loaded {len(documents)} document pages."
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Created {len(chunks)} text chunks."
    )

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )

    print("\nVector database created successfully.")

    return vectorstore


if __name__ == "__main__":

    create_vectorstore()