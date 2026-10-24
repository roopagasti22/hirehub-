"""
Seed script — populates HireHub with realistic sample data.

Usage:
    cd hirehub
    python scripts/seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import MongoDB
import random

app = create_app()

SKILLS_POOL = [
    "python", "javascript", "java", "sql", "mongodb", "react", "node.js",
    "django", "flask", "aws", "docker", "kubernetes", "typescript",
    "postgresql", "redis", "git", "linux", "machine learning", "data analysis",
    "figma", "ui/ux", "golang", "rust", "c++", "spring boot", "angular",
    "vue.js", "graphql", "rest api",
]

COMPANIES = [
    {"name": "TechNova Solutions", "industry": "Technology", "location": "Bengaluru"},
    {"name": "DataBridge Analytics", "industry": "Data Science", "location": "Hyderabad"},
    {"name": "CloudPeak Systems", "industry": "Cloud Computing", "location": "Pune"},
    {"name": "InnovateCo", "industry": "Product", "location": "Mumbai"},
    {"name": "SwiftCode Labs", "industry": "Software Development", "location": "Chennai"},
]

JOB_TITLES = [
    "Senior Python Developer", "Full Stack Engineer", "Data Scientist",
    "DevOps Engineer", "React Frontend Developer", "ML Engineer",
    "Backend API Developer", "Cloud Architect", "Database Administrator",
    "UI/UX Designer", "Node.js Developer", "Java Spring Developer",
    "TypeScript Developer", "Site Reliability Engineer", "Go Developer",
    "Security Engineer", "Mobile Developer", "QA Automation Engineer",
    "Product Manager", "Technical Lead", "Solutions Architect",
    "Django Developer", "Kubernetes Engineer", "Data Engineer",
    "AI Engineer", "GraphQL Developer", "Vue.js Developer",
    "Angular Developer", "Platform Engineer", "Analytics Engineer",
]

LOCATIONS = ["Bengaluru", "Hyderabad", "Pune", "Mumbai", "Chennai", "Delhi", "Noida", "Gurugram"]
WORK_MODES = ["REMOTE", "HYBRID", "ONSITE"]
EMP_TYPES = ["FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT"]
STATUSES = ["OPEN", "OPEN", "OPEN", "CLOSED"]  # weighted towards OPEN


def seed():
    with app.app_context():
        db = MongoDB.get_db()

        # Clear existing data
        for coll in ["users", "companies", "jobs", "applications", "interviews",
                     "resumes", "notifications", "audit_logs"]:
            db[coll].drop()
        print("✓ Cleared existing collections.")

        # ── Create admin ──────────────────────────────────────────────────
        admin_doc = {
            "_id": ObjectId(),
            "name": "Super Admin",
            "email": "admin@hirehub.io",
            "phone": "9000000000",
            "role": "ADMIN",
            "password_hash": generate_password_hash("Admin@1234"),
            "status": "ACTIVE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        db["users"].insert_one(admin_doc)
        print("✓ Admin created  (admin@hirehub.io / Admin@1234)")

        # ── Create recruiters + companies ─────────────────────────────────
        recruiter_ids = []
        company_ids = []

        for i, comp in enumerate(COMPANIES):
            recruiter_id = ObjectId()
            company_id = ObjectId()

            recruiter_doc = {
                "_id": recruiter_id,
                "name": f"Recruiter {i + 1}",
                "email": f"recruiter{i + 1}@hirehub.io",
                "phone": f"900000{i + 1:04d}",
                "role": "RECRUITER",
                "password_hash": generate_password_hash("Recruiter@1234"),
                "status": "ACTIVE",
                "company_id": str(company_id),
                "company_name": comp["name"],
                "designation": "HR Manager",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 90)),
                "updated_at": datetime.utcnow(),
            }
            db["users"].insert_one(recruiter_doc)

            company_doc = {
                "_id": company_id,
                "name": comp["name"],
                "recruiter_id": str(recruiter_id),
                "industry": comp["industry"],
                "website": f"https://www.{comp['name'].lower().replace(' ', '')}.io",
                "description": f"{comp['name']} is a leading {comp['industry'].lower()} company.",
                "location": comp["location"],
                "size": random.choice(["51-200", "201-500", "501-1000"]),
                "logo_url": "",
                "verification_status": "VERIFIED",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(60, 120)),
                "updated_at": datetime.utcnow(),
            }
            db["companies"].insert_one(company_doc)

            recruiter_ids.append(recruiter_id)
            company_ids.append(company_id)

        # Add 5 more recruiters
        for i in range(5, 11):
            comp_idx = random.randint(0, 4)
            recruiter_id = ObjectId()
            recruiter_doc = {
                "_id": recruiter_id,
                "name": f"Recruiter {i}",
                "email": f"recruiter{i}@hirehub.io",
                "phone": f"900000{i:04d}",
                "role": "RECRUITER",
                "password_hash": generate_password_hash("Recruiter@1234"),
                "status": "ACTIVE",
                "company_id": str(company_ids[comp_idx]),
                "company_name": COMPANIES[comp_idx]["name"],
                "designation": "Talent Acquisition",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                "updated_at": datetime.utcnow(),
            }
            db["users"].insert_one(recruiter_doc)
            recruiter_ids.append(recruiter_id)

        print(f"✓ {len(recruiter_ids)} recruiters + {len(company_ids)} companies created.")

        # ── Create candidates ─────────────────────────────────────────────
        candidate_ids = []
        for i in range(1, 21):
            skills = random.sample(SKILLS_POOL, random.randint(3, 8))
            candidate_id = ObjectId()
            candidate_doc = {
                "_id": candidate_id,
                "name": f"Candidate {i}",
                "email": f"candidate{i}@hirehub.io",
                "phone": f"800000{i:04d}",
                "role": "CANDIDATE",
                "password_hash": generate_password_hash("Candidate@1234"),
                "status": "ACTIVE",
                "location": random.choice(LOCATIONS),
                "skills": skills,
                "education": [{"degree": "B.Tech", "institution": "IIT Roorkee", "year": "2020"}],
                "experience": [{"title": "Software Engineer", "company": "Startup X", "years": random.randint(0, 5)}],
                "expected_salary": random.choice([400000, 600000, 800000, 1000000, 1200000]),
                "notice_period": random.choice([15, 30, 60, 90]),
                "resume_id": None,
                "saved_jobs": [],
                "profile_complete": random.randint(50, 100),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                "updated_at": datetime.utcnow(),
            }
            db["users"].insert_one(candidate_doc)
            candidate_ids.append(candidate_id)

            # Welcome notification
            db["notifications"].insert_one({
                "user_id": str(candidate_id),
                "title": "Welcome to HireHub!",
                "message": f"Hi Candidate {i}, your account is ready.",
                "notification_type": "REGISTRATION",
                "is_read": False,
                "created_at": datetime.utcnow(),
            })

        print(f"✓ {len(candidate_ids)} candidates created.")

        # ── Create jobs ───────────────────────────────────────────────────
        job_ids = []
        for i, title in enumerate(JOB_TITLES):
            r_idx = i % len(recruiter_ids)
            c_idx = i % len(company_ids)
            skills = random.sample(SKILLS_POOL, random.randint(3, 7))
            exp_min = random.randint(0, 3)
            exp_max = exp_min + random.randint(1, 4)
            sal_min = random.choice([300000, 500000, 700000, 900000])
            sal_max = sal_min + random.choice([200000, 300000, 500000])
            status = random.choice(STATUSES)

            job_id = ObjectId()
            job_doc = {
                "_id": job_id,
                "title": title,
                "company_id": str(company_ids[c_idx]),
                "recruiter_id": str(recruiter_ids[r_idx]),
                "description": f"We are looking for a skilled {title} to join our growing team. "
                               f"You will work on exciting projects using {', '.join(skills[:3])}.",
                "skills": skills,
                "experience_min": exp_min,
                "experience_max": exp_max,
                "location": random.choice(LOCATIONS),
                "work_mode": random.choice(WORK_MODES),
                "employment_type": random.choice(EMP_TYPES),
                "salary_min": sal_min,
                "salary_max": sal_max,
                "deadline": datetime.utcnow() + timedelta(days=random.randint(10, 60)),
                "status": status,
                "posted_date": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.utcnow(),
            }
            db["jobs"].insert_one(job_doc)
            job_ids.append(job_id)

        print(f"✓ {len(job_ids)} jobs created.")

        # ── Create applications ───────────────────────────────────────────
        app_statuses = ["APPLIED", "UNDER_REVIEW", "SHORTLISTED", "INTERVIEW_SCHEDULED",
                        "SELECTED", "REJECTED", "WITHDRAWN"]
        app_ids = []
        applied_pairs = set()

        for _ in range(50):
            c_id = random.choice(candidate_ids)
            j_id = random.choice(job_ids)
            pair = (str(c_id), str(j_id))
            if pair in applied_pairs:
                continue
            applied_pairs.add(pair)

            status = random.choice(app_statuses)
            app_id = ObjectId()
            app_doc = {
                "_id": app_id,
                "candidate_id": str(c_id),
                "job_id": str(j_id),
                "status": status,
                "recruiter_notes": "Good candidate." if status in ("SHORTLISTED", "SELECTED") else "",
                "interview_id": None,
                "applied_at": datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                "updated_at": datetime.utcnow(),
            }
            db["applications"].insert_one(app_doc)
            app_ids.append((app_id, c_id, j_id, status))

        print(f"✓ {len(app_ids)} applications created.")

        # ── Create interviews ─────────────────────────────────────────────
        interview_count = 0
        for app_id, c_id, j_id, status in app_ids:
            if status in ("INTERVIEW_SCHEDULED", "SELECTED") and interview_count < 15:
                job = db["jobs"].find_one({"_id": j_id})
                iv_id = ObjectId()
                iv_doc = {
                    "_id": iv_id,
                    "application_id": str(app_id),
                    "candidate_id": str(c_id),
                    "recruiter_id": job["recruiter_id"] if job else str(recruiter_ids[0]),
                    "date": datetime.utcnow() + timedelta(days=random.randint(1, 14)),
                    "time": random.choice(["10:00", "11:30", "14:00", "15:30", "16:00"]),
                    "interview_type": random.choice(["ONLINE", "PHONE", "IN_PERSON"]),
                    "meeting_link": "https://meet.google.com/abc-defg-hij" if True else "",
                    "status": random.choice(["SCHEDULED", "COMPLETED"]),
                    "feedback": "Strong candidate, good technical skills." if random.random() > 0.5 else "",
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 5)),
                    "updated_at": datetime.utcnow(),
                }
                db["interviews"].insert_one(iv_doc)
                db["applications"].update_one({"_id": app_id}, {"$set": {"interview_id": str(iv_id)}})
                interview_count += 1

        print(f"✓ {interview_count} interviews created.")
        print("\n── Seed complete! ────────────────────────────────────────────")
        print("Admin:     admin@hirehub.io     / Admin@1234")
        print("Recruiter: recruiter1@hirehub.io / Recruiter@1234")
        print("Candidate: candidate1@hirehub.io / Candidate@1234")
        print("──────────────────────────────────────────────────────────────")


if __name__ == "__main__":
    seed()
