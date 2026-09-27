import os

from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017"
)


client = MongoClient(MONGODB_URI)

db = client["stock_research_assistant"]

research_collection = db["research_reports"]


def save_research_report(report_data: dict):

    # Create a separate copy so MongoDB does not
    # add _id to the original report object.
    document = report_data.copy()

    result = research_collection.insert_one(document)

    return str(result.inserted_id)


def get_research_history():

    reports = research_collection.find().sort(
        "created_at",
        -1
    )

    results = []

    for report in reports:

        report["_id"] = str(report["_id"])

        results.append(report)

    return results