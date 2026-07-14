import instructor
from groq import Groq
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from core.state import JobHunterState
from core.models import StructuredJob, CompanyIntel, ColdEmailDraft, SkillGapPlan, InterviewPlaybook, TailoredResume
import os
client = instructor.from_groq(Groq())

def scrape_job_node(state: JobHunterState):
    url = state.get("raw_job_url")
    if not url or url == "N/A" or not url.startswith("http"):
        return {"error_logs": ["No valid URL provided; using manual text input."]}
    
    print(f"🕸️ Scraping job posting from: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        print(f"⚠️ requests failed: {e}. Falling back to Playwright...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_load_state('networkidle')
                html_content = page.content()
                browser.close()
        except Exception as pw_e:
            return {"error_logs": [f"Scraping failed (Requests & Playwright): {str(pw_e)}"]}

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for noise in soup(['script', 'style', 'nav', 'footer', 'header']):
            noise.decompose()
        clean_markdown = markdownify(str(soup), heading_style="ATX").strip()
        return {"raw_job_html": clean_markdown}
    except Exception as e:
        return {"error_logs": [f"Scraping parsing failed: {str(e)}"]}

def extract_jd_node(state: JobHunterState):
    try:
        job_data = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=StructuredJob,
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter."},
                {"role": "user", "content": f"Extract details from this JD text:\n{state.get('raw_job_html', '')}"}
            ]
        )
        return {"structured_job": job_data}
    except Exception as e:
        return {"error_logs": [f"JD Extraction Failed: {str(e)}"]}

def retrieve_context_node(state: JobHunterState):
    job = state.get("structured_job")
    if not job:
        return {"error_logs": ["No job data found."]}
        
    resume_path = "data/master_resume.txt"
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            full_resume = f.read()
    else:
        full_resume = "Software Engineer with experience in Python and Backend systems."
        
    return {"user_resume_context": full_resume}

def gather_intel_node(state: JobHunterState):
    job = state.get("structured_job")
    if not job or not job.company_name or job.company_name == "Not Available":
        return {"company_intel": CompanyIntel(recent_news=["No company provided"], tech_stack_clues=["N/A"], market_position="N/A")}
    print(f"🕵️‍♂️ Searching the web for {job.company_name}...")
    try:
        results = DDGS().text(f"{job.company_name} recent news engineering blog tech stack", max_results=3)
        search_context = "\n".join([f"- {res['title']}: {res['body']}" for res in results])
    except Exception as e:
        search_context = f"Search failed: {str(e)}"
    
    intel_data = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_model=CompanyIntel,
        messages=[
            {"role": "system", "content": "Extract company intel from the search results provided. Be concise."},
            {"role": "user", "content": f"Search Results for {job.company_name}:\n{search_context}"}
        ]
    )
    return {"company_intel": intel_data}

def draft_email_node(state: JobHunterState):
    job = state.get("structured_job")
    intel = state.get("company_intel")
    resume = state.get("user_resume_context")
    prompt = f"""Write a cold email to the hiring manager for {job.role_title} at {job.company_name}.
    Company Context: {intel.recent_news}
    My Relevant Background: {resume}
    Connect my specific background to their context directly. Keep it under 150 words."""
    email_draft = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=ColdEmailDraft,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"drafted_email": email_draft}

def generate_plan_node(state: JobHunterState):
    job = state.get("structured_job")
    resume = state.get("user_resume_context")
    prompt = f"""Compare my background to the job requirements for {job.role_title}.
    Job Skills Needed: {[s.skill for s in job.core_skills]}
    My Background: {resume}
    Identify the gaps and build a 7-day upskilling plan."""
    plan = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=SkillGapPlan,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"skill_gap_plan": plan}

def prep_interview_node(state: JobHunterState):
    job = state.get("structured_job")
    intel = state.get("company_intel")
    resume = state.get("user_resume_context")
    plan = state.get("skill_gap_plan")
    missing = plan.missing_skills if plan else ["Unknown gaps"]
    prompt = f"""Act as a rigorous Principal Engineer at {job.company_name} interviewing a candidate for {job.role_title}.
    Company News: {intel.recent_news}
    Candidate's Resume Context: {resume}
    Candidate's Weaknesses (Skill Gaps): {missing}
    Generate the exact technical and behavioral questions you would ask them."""
    playbook = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=InterviewPlaybook,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"interview_playbook": playbook}

# --- NEW NODE: Resume Tailor ---
def tailor_resume_node(state: JobHunterState):
    job = state.get("structured_job")
    resume = state.get("user_resume_context")
    prompt = f"""You are an expert Resume Writer optimizing for ATS systems.
    Job Title: {job.role_title}
    Required Skills: {[s.skill for s in job.core_skills]}
    My Actual Experience: {resume}
    
    Rewrite my professional summary and my top 5 bullet points to naturally integrate the required skills. 
    DO NOT INVENT EXPERIENCE I DO NOT HAVE. Rephrase my existing work to sound highly relevant to this specific role."""
    
    tailored = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=TailoredResume,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"tailored_resume": tailored}