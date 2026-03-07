"""
Seed script for FCI Investigation Platform.

Populates MongoDB with mock user accounts.
Cases are created through the ingestion pipeline, not seeded.

Usage: python scripts/seed_demo_data.py

Requires: MongoDB running on localhost:27017
"""

from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"


USERS = [
    {
        "_id": "user_001",
        "username": "ben.investigator",
        "display_name": "Ben",
        "created_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
    },
    {
        "_id": "user_002",
        "username": "demo.investigator",
        "display_name": "Demo User",
        "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc),
    },
]


def seed():
    """Connect to MongoDB and seed user accounts."""
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Clear existing data
    print("Dropping existing collections...")
    db.users.drop()
    db.cases.drop()
    db.conversations.drop()

    # Seed users
    db.users.insert_many(USERS)
    print(f"Seeded {len(USERS)} users")

    # Verify
    print("\nVerification:")
    print(f"  Users: {db.users.count_documents({})}")
    print(f"  Cases: {db.cases.count_documents({})}")
    print(f"  Conversations: {db.conversations.count_documents({})}")

    client.close()
    print("\nDone. User accounts seeded successfully.")


if __name__ == "__main__":
    seed()
