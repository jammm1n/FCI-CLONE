"""
Seed script for FCI Investigation Platform.

Populates MongoDB with user accounts (with bcrypt-hashed passwords).
Cases are created through the ingestion pipeline, not seeded.

Usage: python scripts/seed_demo_data.py

Requires: MongoDB running on localhost:27017
"""

import bcrypt
from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


USERS = [
    {
        "_id": "user_001",
        "username": "ben.investigator",
        "display_name": "Ben",
        "password_hash": hash_pw("ben123"),
        "created_at": datetime(2026, 1, 15, tzinfo=timezone.utc),
    },
    {
        "_id": "user_002",
        "username": "demo.investigator",
        "display_name": "Demo User",
        "password_hash": hash_pw("demo123"),
        "created_at": datetime(2026, 2, 1, tzinfo=timezone.utc),
    },
]


def seed():
    """Connect to MongoDB and seed user accounts."""
    print(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Only reseed users — preserve cases and conversations
    print("Dropping users collection...")
    db.users.drop()

    # Seed users
    db.users.insert_many(USERS)
    print(f"Seeded {len(USERS)} users")

    # Print credentials for reference
    print("\nCredentials:")
    print("  ben.investigator / ben123")
    print("  demo.investigator / demo123")

    # Verify
    print(f"\nVerification:")
    print(f"  Users: {db.users.count_documents({})}")
    print(f"  Cases: {db.cases.count_documents({})}")
    print(f"  Conversations: {db.conversations.count_documents({})}")

    client.close()
    print("\nDone. User accounts seeded successfully.")


if __name__ == "__main__":
    seed()
