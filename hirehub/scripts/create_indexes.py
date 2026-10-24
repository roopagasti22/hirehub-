"""
Index creation script for HireHub MongoDB collections.

Usage:
    cd hirehub
    python scripts/create_indexes.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import ASCENDING, DESCENDING, TEXT
from app import create_app
from app.extensions import MongoDB

app = create_app()


def create_indexes():
    with app.app_context():
        db = MongoDB.get_db()

        # ── users collection ──────────────────────────────────────────────
        db["users"].create_index([("email", ASCENDING)], unique=True)
        db["users"].create_index([("role", ASCENDING)])
        db["users"].create_index([("status", ASCENDING)])
        db["users"].create_index([("created_at", DESCENDING)])
        print("✓ users indexes")

        # ── companies collection ──────────────────────────────────────────
        db["companies"].create_index([("recruiter_id", ASCENDING)])
        db["companies"].create_index([("verification_status", ASCENDING)])
        db["companies"].create_index([("name", ASCENDING)])
        print("✓ companies indexes")

        # ── jobs collection ───────────────────────────────────────────────
        db["jobs"].create_index([("title", ASCENDING)])
        db["jobs"].create_index([("skills", ASCENDING)])
        db["jobs"].create_index([("location", ASCENDING)])
        db["jobs"].create_index([("status", ASCENDING)])
        db["jobs"].create_index([("recruiter_id", ASCENDING)])
        db["jobs"].create_index([("company_id", ASCENDING)])
        db["jobs"].create_index([("posted_date", DESCENDING)])
        db["jobs"].create_index([("work_mode", ASCENDING)])
        db["jobs"].create_index([("employment_type", ASCENDING)])
        # Text index for keyword search
        db["jobs"].create_index([("title", TEXT), ("description", TEXT)])
        print("✓ jobs indexes")

        # ── applications collection ───────────────────────────────────────
        db["applications"].create_index([("candidate_id", ASCENDING)])
        db["applications"].create_index([("job_id", ASCENDING)])
        db["applications"].create_index(
            [("candidate_id", ASCENDING), ("job_id", ASCENDING)], unique=True
        )
        db["applications"].create_index([("status", ASCENDING)])
        db["applications"].create_index([("applied_at", DESCENDING)])
        print("✓ applications indexes")

        # ── interviews collection ─────────────────────────────────────────
        db["interviews"].create_index([("candidate_id", ASCENDING)])
        db["interviews"].create_index([("recruiter_id", ASCENDING)])
        db["interviews"].create_index([("application_id", ASCENDING)])
        db["interviews"].create_index([("date", ASCENDING)])
        print("✓ interviews indexes")

        # ── resumes collection ────────────────────────────────────────────
        db["resumes"].create_index([("candidate_id", ASCENDING)], unique=True)
        print("✓ resumes indexes")

        # ── notifications collection ──────────────────────────────────────
        db["notifications"].create_index([("user_id", ASCENDING)])
        db["notifications"].create_index([("is_read", ASCENDING)])
        db["notifications"].create_index([("created_at", DESCENDING)])
        print("✓ notifications indexes")

        # ── audit_logs collection ─────────────────────────────────────────
        db["audit_logs"].create_index([("user_id", ASCENDING)])
        db["audit_logs"].create_index([("action", ASCENDING)])
        db["audit_logs"].create_index([("timestamp", DESCENDING)])
        print("✓ audit_logs indexes")

        print("\n── All indexes created successfully! ────────────────────────")


if __name__ == "__main__":
    create_indexes()
