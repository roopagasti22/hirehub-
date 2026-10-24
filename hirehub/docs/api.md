# HireHub REST API Reference

Base URL: `http://localhost:5000/api`

All responses follow:

```json
{ "success": true, "message": "...", "data": {} }
{ "success": false, "message": "...", "error_code": "..." }
```

---

## Authentication

| Method | Endpoint          | Auth     | Description          |
|--------|-------------------|----------|----------------------|
| POST   | /auth/register    | Public   | Register candidate/recruiter |
| POST   | /auth/login       | Public   | Login                |
| POST   | /auth/logout      | Public   | Logout               |
| GET    | /auth/me          | Required | Get current user     |

### Register

```json
POST /api/auth/register
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "9876543210",
  "password": "Test@1234",
  "confirm_password": "Test@1234",
  "role": "CANDIDATE"
}
```

---

## Jobs

| Method | Endpoint       | Auth         | Description       |
|--------|----------------|--------------|-------------------|
| GET    | /jobs/         | Public       | List/search jobs  |
| GET    | /jobs/:id      | Public       | Get job details   |
| POST   | /jobs/         | RECRUITER    | Create job        |
| PUT    | /jobs/:id      | RECRUITER    | Update job        |
| DELETE | /jobs/:id      | RECRUITER    | Close job         |
| POST   | /jobs/:id/apply| CANDIDATE    | Apply to job      |

### Search Parameters

```
GET /api/jobs/?q=python&location=bengaluru&work_mode=HYBRID&skill=django,flask&page=1&per_page=10
```

---

## Candidates

| Method | Endpoint            | Auth      | Description        |
|--------|---------------------|-----------|--------------------|
| GET    | /candidates/:id     | Required  | Get profile        |
| PUT    | /candidates/:id     | CANDIDATE | Update profile     |

---

## Applications

| Method | Endpoint                  | Auth           | Description            |
|--------|---------------------------|----------------|------------------------|
| GET    | /applications/            | Required       | List applications      |
| GET    | /applications/:id         | Required       | Get application        |
| PUT    | /applications/:id/status  | RECRUITER      | Update status          |
| POST   | /applications/:id/withdraw| CANDIDATE      | Withdraw application   |

---

## Interviews

| Method | Endpoint        | Auth       | Description         |
|--------|-----------------|------------|---------------------|
| POST   | /interviews/    | RECRUITER  | Schedule interview  |
| GET    | /interviews/    | Required   | List interviews     |
| PUT    | /interviews/:id | RECRUITER  | Update interview    |

---

## Resumes

| Method | Endpoint        | Auth       | Description       |
|--------|-----------------|------------|-------------------|
| POST   | /resumes/       | CANDIDATE  | Upload resume     |
| GET    | /resumes/:id    | Required   | Download resume   |
| DELETE | /resumes/:id    | CANDIDATE  | Delete resume     |

---

## Analytics

| Method | Endpoint              | Auth       |
|--------|-----------------------|------------|
| GET    | /analytics/candidate  | CANDIDATE  |
| GET    | /analytics/recruiter  | RECRUITER  |
| GET    | /analytics/admin      | ADMIN      |
