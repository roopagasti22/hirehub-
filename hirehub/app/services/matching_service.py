"""Rule-based job–candidate matching service."""
from __future__ import annotations
from typing import Optional


class MatchingService:
    """
    Calculates a match score between a candidate and a job
    using a rule-based algorithm (no ML).

    Score components:
      - Skills match:      50 points
      - Location match:    15 points
      - Work mode match:   10 points
      - Experience match:  15 points
      - Salary match:      10 points
    """

    WEIGHTS = {
        "skills": 50,
        "location": 15,
        "work_mode": 10,
        "experience": 15,
        "salary": 10,
    }

    def calculate(self, candidate: dict, job: dict) -> dict:
        """Return a detailed match result dict."""
        score = 0
        breakdown = {}

        # ── Skills ───────────────────────────────────────────────────────
        candidate_skills = {s.strip().lower() for s in (candidate.get("skills") or [])}
        job_skills = {s.strip().lower() for s in (job.get("skills") or [])}

        matched_skills = sorted(candidate_skills & job_skills)
        missing_skills = sorted(job_skills - candidate_skills)

        if job_skills:
            skill_ratio = len(matched_skills) / len(job_skills)
        else:
            skill_ratio = 1.0

        skill_points = round(self.WEIGHTS["skills"] * skill_ratio)
        score += skill_points
        breakdown["skills"] = {
            "score": skill_points,
            "max": self.WEIGHTS["skills"],
            "matched": matched_skills,
            "missing": missing_skills,
        }

        # ── Location ─────────────────────────────────────────────────────
        c_location = (candidate.get("location") or "").strip().lower()
        j_location = (job.get("location") or "").strip().lower()
        location_match = bool(c_location and j_location and (
            c_location in j_location or j_location in c_location
        ))
        # Remote jobs always match location
        if job.get("work_mode", "").upper() == "REMOTE":
            location_match = True

        loc_points = self.WEIGHTS["location"] if location_match else 0
        score += loc_points
        breakdown["location"] = {"score": loc_points, "max": self.WEIGHTS["location"], "match": location_match}

        # ── Work mode ────────────────────────────────────────────────────
        # Candidates don't store preferred work mode yet; give full points
        wm_points = self.WEIGHTS["work_mode"]
        score += wm_points
        breakdown["work_mode"] = {"score": wm_points, "max": self.WEIGHTS["work_mode"]}

        # ── Experience ───────────────────────────────────────────────────
        candidate_exp = self._total_experience_years(candidate.get("experience") or [])
        # Cast to int — MongoDB may return strings if data was inserted as strings
        try:
            exp_min = int(job.get("experience_min") or 0)
        except (TypeError, ValueError):
            exp_min = 0
        try:
            exp_max = int(job.get("experience_max") or 99)
        except (TypeError, ValueError):
            exp_max = 99
        if exp_max == 0:
            exp_max = 99

        if exp_min <= candidate_exp <= exp_max:
            exp_points = self.WEIGHTS["experience"]
        elif candidate_exp >= exp_min:
            exp_points = round(self.WEIGHTS["experience"] * 0.7)  # overqualified partial
        else:
            deficit = exp_min - candidate_exp
            ratio = max(0, 1 - deficit / max(exp_min, 1))
            exp_points = round(self.WEIGHTS["experience"] * ratio)

        score += exp_points
        breakdown["experience"] = {
            "score": exp_points,
            "max": self.WEIGHTS["experience"],
            "candidate_years": candidate_exp,
            "required_range": [exp_min, exp_max],
        }

        # ── Salary ───────────────────────────────────────────────────────
        try:
            candidate_salary = int(candidate.get("expected_salary") or 0)
        except (TypeError, ValueError):
            candidate_salary = 0
        try:
            sal_min = int(job.get("salary_min") or 0)
        except (TypeError, ValueError):
            sal_min = 0
        try:
            sal_max = int(job.get("salary_max") or 0)
        except (TypeError, ValueError):
            sal_max = 0

        if sal_max > 0 and candidate_salary > 0:
            if sal_min <= candidate_salary <= sal_max:
                sal_points = self.WEIGHTS["salary"]
            elif candidate_salary <= sal_max:
                sal_points = round(self.WEIGHTS["salary"] * 0.7)
            else:
                sal_points = 0
        else:
            sal_points = self.WEIGHTS["salary"]  # no salary info — no penalty

        score += sal_points
        breakdown["salary"] = {"score": sal_points, "max": self.WEIGHTS["salary"]}

        return {
            "score": score,
            "percentage": score,  # max is 100
            "breakdown": breakdown,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        }

    @staticmethod
    def _total_experience_years(experience_list: list) -> int:
        """Estimate total years of experience from the candidate's experience list."""
        total = 0
        for exp in experience_list:
            years = exp.get("years") or exp.get("duration_years") or 0
            try:
                total += int(years)
            except (TypeError, ValueError):
                pass
        return total
