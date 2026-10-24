# HireHub — Job Hiring & Recruitment Portal

A fully functional, modular recruitment platform built with Python/Flask, MongoDB, and Bootstrap 5.

---

## Features

- Three roles: **Candidate**, **Recruiter**, **Admin**
- JWT-free session-based auth with password hashing
- Job posting, search, filtering, and pagination
- Resume upload/download (PDF, DOC, DOCX)
- Application tracking with status transitions
- Interview scheduling with notifications
- Rule-based job–candidate matching (skill, location, experience, salary)
- Personalised job recommendations
- Analytics dashboards with Chart.js
- CSV reports with date/status filters
- Full audit log trail
- REST API (JSON responses)
- Responsive Bootstrap 5 UI

---

## Quick Start

### 1. Prerequisites

- Python 3.12+
- MongoDB running locally (`mongodb://localhost:27017`)

### 2. Install dependencies

```bash
cd hirehub
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY, MONGO_URI, etc.
```

### 4. Create indexes

```bash
python scripts/create_indexes.py
```

### 5. Seed sample data (optional)

```bash
python scripts/seed_data.py
```

Seed credentials:

| Role      | Email                      | Password         |
|-----------|----------------------------|------------------|
| Admin     | admin@hirehub.io           | Admin@1234       |
| Recruiter | recruiter1@hirehub.io      | Recruiter@1234   |
| Candidate | candidate1@hirehub.io      | Candidate@1234   |

### 6. Run the application

```bash
python run.py
```

Visit: http://localhost:5000

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
hirehub/
├── run.py                   # App entry point
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Config classes
│   ├── extensions.py        # MongoDB wrapper
│   ├── models/              # Domain objects (OOP)
│   ├── repositories/        # DB layer
│   ├── services/            # Business logic
│   ├── routes/
│   │   ├── web/             # HTML routes
│   │   └── api/             # REST API routes
│   ├── utils/               # Validators, decorators, helpers
│   ├── exceptions/          # Custom exceptions
│   ├── middleware/          # Error handlers
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS
├── tests/                   # pytest test suite
└── scripts/                 # seed_data.py, create_indexes.py
```

---

## Architecture

```
Routes  →  Services  →  Repositories  →  MongoDB
```

- **Routes**: HTTP concerns only (parse request, call service, render/return)
- **Services**: Business logic, validation, orchestration
- **Repositories**: MongoDB queries, CRUD
- **Models**: Domain objects with OOP (inheritance, properties, etc.)
