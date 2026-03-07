"""
User management CLI for FCI Investigation Platform.

Usage:
  python scripts/manage_user.py list
  python scripts/manage_user.py add <username> <display_name> <password>
  python scripts/manage_user.py password <username> <new_password>
  python scripts/manage_user.py delete <username>

Examples:
  python scripts/manage_user.py add jane.investigator Jane secret123
  python scripts/manage_user.py password ben.investigator newpass456
  python scripts/manage_user.py list
  python scripts/manage_user.py delete demo.investigator
"""

import sys
import bcrypt
from pymongo import MongoClient
from datetime import datetime, timezone

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fci_platform"


def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def cmd_list():
    db = get_db()
    users = list(db.users.find({}, {"_id": 1, "username": 1, "display_name": 1, "created_at": 1}))
    if not users:
        print("No users found.")
        return
    print(f"{'ID':<12} {'Username':<25} {'Display Name':<20} {'Created'}")
    print("-" * 80)
    for u in users:
        created = u.get("created_at", "")
        if isinstance(created, datetime):
            created = created.strftime("%Y-%m-%d")
        print(f"{u['_id']:<12} {u['username']:<25} {u.get('display_name', ''):<20} {created}")


def cmd_add(username: str, display_name: str, password: str):
    db = get_db()
    existing = db.users.find_one({"username": username})
    if existing:
        print(f"Error: User '{username}' already exists (ID: {existing['_id']})")
        sys.exit(1)

    # Auto-generate user ID
    max_user = db.users.find_one(sort=[("_id", -1)])
    if max_user and max_user["_id"].startswith("user_"):
        try:
            num = int(max_user["_id"].split("_")[1]) + 1
        except ValueError:
            num = 1
    else:
        num = 1
    user_id = f"user_{num:03d}"

    doc = {
        "_id": user_id,
        "username": username,
        "display_name": display_name,
        "password_hash": hash_pw(password),
        "created_at": datetime.now(timezone.utc),
    }
    db.users.insert_one(doc)
    print(f"Created user: {username} (ID: {user_id}, display: {display_name})")


def cmd_password(username: str, new_password: str):
    db = get_db()
    result = db.users.update_one(
        {"username": username},
        {"$set": {"password_hash": hash_pw(new_password)}},
    )
    if result.matched_count == 0:
        print(f"Error: User '{username}' not found")
        sys.exit(1)
    print(f"Password updated for {username}")


def cmd_delete(username: str):
    db = get_db()
    user = db.users.find_one({"username": username})
    if not user:
        print(f"Error: User '{username}' not found")
        sys.exit(1)

    confirm = input(f"Delete user '{username}' (ID: {user['_id']})? This does NOT delete their cases. [y/N] ")
    if confirm.lower() != "y":
        print("Cancelled.")
        return

    db.users.delete_one({"_id": user["_id"]})
    print(f"Deleted user: {username}")


USAGE = __doc__.strip()

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        sys.exit(1)

    cmd = args[0]

    if cmd == "list":
        cmd_list()
    elif cmd == "add":
        if len(args) != 4:
            print("Usage: manage_user.py add <username> <display_name> <password>")
            sys.exit(1)
        cmd_add(args[1], args[2], args[3])
    elif cmd == "password":
        if len(args) != 3:
            print("Usage: manage_user.py password <username> <new_password>")
            sys.exit(1)
        cmd_password(args[1], args[2])
    elif cmd == "delete":
        if len(args) != 2:
            print("Usage: manage_user.py delete <username>")
            sys.exit(1)
        cmd_delete(args[1])
    else:
        print(f"Unknown command: {cmd}\n")
        print(USAGE)
        sys.exit(1)
