# HireHub Architecture

## Layered Architecture

```
HTTP Request
     │
     ▼
┌─────────────────────────┐
│   Routes (Blueprints)   │  ← HTTP concerns: parse, validate format, respond
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Services           │  ← Business logic, orchestration, notifications
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Repositories        │  ← MongoDB queries, CRUD, aggregations
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       MongoDB           │  ← Persistent storage
└─────────────────────────┘
```

## Blueprint Structure

- `web_bp` — HTML/Jinja2 web routes
  - `auth_bp`       — /auth/login, /auth/register, /auth/logout
  - `candidate_bp`  — /candidate/...
  - `recruiter_bp`  — /recruiter/...
  - `admin_bp`      — /admin/...
  - `jobs_bp`       — /jobs/...
  - `dashboard_bp`  — /dashboard/...

- `api_bp` — REST API (JSON)
  - `auth_api_bp`       — /api/auth/...
  - `job_api_bp`        — /api/jobs/...
  - `candidate_api_bp`  — /api/candidates/...
  - `application_api_bp`— /api/applications/...
  - `interview_api_bp`  — /api/interviews/...
  - `resume_api_bp`     — /api/resumes/...
  - `analytics_api_bp`  — /api/analytics/...
  - `admin_api_bp`      — /api/admin/...

## OOP Design

```
User (base)
  ├── Candidate   — skills, education, experience, saved_jobs
  ├── Recruiter   — company_id, designation
  └── Admin       — admin-only operations

Standalone domain classes:
  Company, Job, Application, Interview, Resume, Notification
```

## Key Design Decisions

1. **Application factory** (`create_app()`) — supports testing/production configs
2. **Repository pattern** — all MongoDB calls isolated from services
3. **BaseRepository** — abstract class with shared CRUD helpers
4. **Dependency injection** — services receive repos via constructor
5. **Custom exceptions** — mapped to HTTP codes in middleware
6. **Session-based auth** — Flask session + Werkzeug password hashing
7. **Rule-based matching** — MatchingService (no ML dependencies)
