# 🎯 Agentic Job Hunter

An autonomous, multi-agent AI pipeline designed to source, evaluate, and apply to tech jobs with surgical precision.

## ❓ Why It Was Built

Job hunting in the modern tech landscape is broken. Applying to hundreds of roles manually is soul-crushing, and traditional "spray and pray" bots send generic resumes that get instantly rejected by ATS (Applicant Tracking Systems). 

This project was built to solve the **quality vs. quantity** dilemma. It automates the tedious parts of finding jobs, but uses high-level LLM reasoning to ensure every application is highly targeted, deeply researched, and perfectly tailored to the specific company.

## 🚀 How It Is Different

Unlike standard web scrapers or blind auto-appliers, the Agentic Job Hunter uses a **Sidecar Architecture** and a **Two-Pass AI Filter**:

1. **Multi-Source Intelligence:** It doesn't rely on a single brittle search engine. It natively aggregates jobs from GitHub Internship repos, HackerNews "Who is hiring?" threads, the RemoteOK API, and intercepts LinkedIn/Indeed alerts directly from your Gmail inbox.
2. **The Ruthless Bouncer:** Instead of applying to everything, the AI "Bouncer" aggressively filters out Senior, Lead, or Staff roles, ensuring you only spend time on jobs that match your experience level (Internship/Junior).
3. **Whole-Document Ingestion:** It abandons flawed vector-based RAG matching. Instead, it injects your *entire* master resume into the LLM context window to guarantee zero hallucination when tailoring your skills to a job description.
4. **Native Browser Injection (Sidecar):** Instead of using heavy, breakable headless browsers (like Playwright), this tool utilizes a custom Chrome Extension that talks to a FastAPI backend. You browse the web normally, and the AI injects tailored emails and resumes directly into your active tab.

## 🏗️ Architecture (How it Works)

The system is broken into four main components:
*   **The Sniper (`sniper.py`)**: A background worker that runs on a schedule (via GitHub Actions) to source jobs from across the internet, grade them against your resume, and ping your Discord if a high-match job is found.
*   **The Brain (`agent/workflow.py`)**: A LangGraph state machine powered by Llama-3 (via Groq). It extracts Job Descriptions, searches the web for company intel, drafts cold emails, and generates technical interview playbooks.
*   **The Backend (`api.py`)**: A FastAPI server that exposes the LangGraph brain to the internet.
*   **The Frontend (`extension/` & `app.py`)**: A custom Chrome Extension for real-time browsing, and a glassmorphic Streamlit Control Room for managing your SQLite database of tracked jobs.

---

## 🛠️ How to Use This Application

### 1. Prerequisites
*   Python 3.11+
*   A [Groq API Key](https://console.groq.com/keys) (Free)
*   A Discord Server Webhook URL
*   A Google Cloud project with Gmail API enabled (for `credentials.json`)

### 2. Local Setup (Security & Environment Variables)
Clone the repository and install dependencies:
```bash
git clone https://github.com/YOUR_USERNAME/agentic-job-hunter.git
cd agentic-job-hunter
pip install -r requirements.txt
```

**⚠️ IMPORTANT:** For security reasons, API keys and credentials are NOT uploaded to GitHub. If you are cloning this project, you must manually create the following files in the root folder before running the app.

1. **The `.env` file:** Create a new file named `.env` in the root directory and add your keys:
```env
GROQ_API_KEY=your_groq_key
DISCORD_WEBHOOK_URL=your_discord_webhook
MY_RESUME_TEXT="Your full, detailed resume goes here..."
```

2. **The `credentials.json` file (For Gmail Integration):**
   * Go to the [Google Cloud Console](https://console.cloud.google.com/).
   * Enable the Gmail API and generate an OAuth 2.0 Client ID for a Desktop Application.
   * Download the JSON file, rename it exactly to `credentials.json`, and place it in the root folder.
   * *(Note: When you run the script for the first time, a browser window will open asking you to log in to Google. Once you approve, it will automatically generate a `token.json` file which saves your login state).*

### 3. Running the Control Room (Streamlit)
To view your dashboard, tracked jobs, and AI playbooks:
```bash
streamlit run app.py
```

### 4. Running the Chrome Extension Sidecar
1. Start the FastAPI backend:
   ```bash
   uvicorn api:app --reload
   ```
2. Open Chrome and navigate to `chrome://extensions/`.
3. Toggle **Developer Mode** on.
4. Click **Load unpacked** and select the `extension/` folder from this project.
5. Browse to any job posting (e.g., Greenhouse or LinkedIn), click the extension icon, and hit "Analyze Job".

### 5. Cloud Autopilot (GitHub Actions)
This project includes a `.github/workflows/sniper.yml` file to run the job sourcing agent automatically every 3 days.
1. Push this code to a **Private** GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add your `GROQ_API_KEY`, `DISCORD_WEBHOOK_URL`, and `MY_RESUME_TEXT` as secrets.
4. Add `GMAIL_TOKEN_JSON_BASE64` (Base64 encode your local `token.json` file to allow GitHub to read your job alert emails).

## ⚠️ Disclaimer
This tool uses AI to augment your job search. You should always manually review AI-generated cold emails and tailored resumes before sending them to recruiters.
