# Smart Resume Analyser

AI-powered resume analysis and job-matching platform with separate candidate and recruiter portals. Upload resumes (PDF/DOCX), get an AI-generated score and skill-gap analysis, and discover personalized job matches.

## Table of contents
- [Overview](#overview)
- [Key features](#key-features)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Seeding sample data](#seeding-sample-data)
- [Project structure (brief)](#project-structure-brief)
- [Contributing](#contributing)
- [License](#license)

## Overview

Smart Resume Analyser helps candidates improve resumes and helps recruiters discover, shortlist, and review candidates faster using automated parsing, scoring, and matching.

Core functionality:
- Resume upload and parsing (PDF / DOCX)
- Resume scoring (content, ATS compatibility, formatting)
- Skill-gap analysis and recommendations
- Job matching and ranked matches
- Candidate & recruiter dashboards, shortlist features, and analytics

## Key features
- Upload and parse resumes (PyPDF2, python-docx)
- AI-driven resume score and detailed feedback
- Skill extraction and gap recommendations
- Job matching & recommendations service
- Candidate resume history and versioning
- Recruiter portal: applicants, shortlist, and job management
- Analytics dashboards with charts (Chart.js)

## Tech stack
- Python 3.8+
- Flask (app factory + Blueprints)
- MongoDB (PyMongo)
- spaCy (NLP), PyPDF2, python-docx
- Bootstrap 5, Bootstrap Icons, Chart.js
- Flask-Login for auth, Flask-WTF for forms

## Quick start

1. Clone the repo and enter the directory:

```bash
git clone <repo-url>
cd SmartResumeAnalyser
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Download spaCy model used by the parser:

```bash
python -m spacy download en_core_web_sm
```

5. Create a `.env` file (see Configuration below) and then run:

```bash
python run.py
```

Open http://localhost:5000 in your browser.

## Configuration

Create a `.env` file in the project root with at least the following variables:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
MONGO_URI=mongodb://localhost:27017/smart_resume_analyser
JWT_SECRET_KEY=your-jwt-secret
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
```

Adjust values for production (use HTTPS, secure cookies, and a production-ready database).

## Seeding sample data

To populate the database with demo/sample data and a test account (if seed script supports it):

```bash
python seed_data.py
```

If `seed_data.py` creates default accounts, check the script for credentials. (You can create a recruiter user or use your own.)

## Project structure (brief)

- `app/` — application package (blueprints, models, services, templates, static)
- `run.py` — app entry point
- `requirements.txt` — Python dependencies
- `seed_data.py` — optional sample data loader

Templates, routes, and services are organized under `app/` using Blueprints and a service layer for parsing, recommendations, and analytics.

---
