import os
import asyncio
import aiohttp

import instructor
from groq import AsyncGroq
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import urllib.parse
import re
from agent.gmail_service import get_job_alerts

load_dotenv()
client = instructor.from_groq(AsyncGroq(api_key=os.getenv("GROQ_API_KEY")))

class BouncerDecision(BaseModel):
    is_valid: bool = Field(..., description="True if it's an internship or junior role, False if it requires 3+ years experience or is senior.")
    reason: str = Field(..., description="1 sentence reason for the decision.")

class AnalystScore(BaseModel):
    score: int = Field(..., description="Score from 0 to 100 based on resume fit.")
    pitch: str = Field(..., description="2-sentence pitch on why the candidate is a perfect fit.")

async def get_jobs_from_api(tags: str):
    """Fetches real-time structured JSON data from a Job API (e.g. RemoteOK)"""
    print(f"🕵️‍♂️ Scouting the remote APIs for: {tags}...")
    url = f"https://remoteok.com/api?tag={tags}"
    headers = {"User-Agent": "JobHunter/1.0"}
    all_results = []
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    # The first item in remoteok API is legal info, skip it
                    for item in data[1:11]: # Grab top 10 recent
                        if 'position' in item and 'company' in item:
                            all_results.append({
                                'title': item['position'] + f" @ {item['company']}",
                                'body': item.get('description', '')[:500], # Send snippet to save tokens
                                'href': item.get('url', '')
                            })
        except Exception as e:
            print(f"❌ API fetch failed: {e}")
            
    return all_results

async def source_hackernews():
    print("🕵️‍♂️ Scouting HackerNews 'Who is Hiring?'...")
    url = 'http://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query="Who is hiring?"'
    all_results = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data['hits']: return []
                    latest_post_id = data['hits'][0]['objectID']
                    
                    comments_url = f"http://hn.algolia.com/api/v1/items/{latest_post_id}"
                    async with session.get(comments_url) as c_response:
                        if c_response.status == 200:
                            c_data = await c_response.json()
                            for child in c_data.get('children', [])[:15]:
                                text = child.get('text', '')
                                if text and ('python' in text.lower() or 'backend' in text.lower()):
                                    all_results.append({
                                        'title': f"HN Startup Job (ID: {child.get('id')})",
                                        'body': text[:500],
                                        'href': f"https://news.ycombinator.com/item?id={child.get('id')}"
                                    })
        except Exception as e:
            print(f"❌ HN fetch failed: {e}")
    return all_results

async def source_github():
    print("🕵️‍♂️ Scouting GitHub Internship Repos...")
    url = "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md"
    all_results = []
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.split('\n')
                    for line in lines[:200]:
                        if '|' in line and 'http' in line and ('Python' in line or 'Backend' in line or 'Software' in line):
                            links = re.findall(r'href="([^"]+)"', line) or re.findall(r'\((http[^)]+)\)', line)
                            if links:
                                all_results.append({
                                    'title': "GitHub Sourced Role",
                                    'body': line,
                                    'href': links[0]
                                })
        except Exception as e:
            print(f"❌ GitHub fetch failed: {e}")
    return all_results

async def source_gmail():
    print("🕵️‍♂️ Intercepting Gmail for Job Alerts...")
    urls = get_job_alerts()
    all_results = []
    for url in urls:
        all_results.append({
            'title': "LinkedIn/Indeed Alert",
            'body': "Job alert sourced from your Gmail Inbox.",
            'href': url
        })
    return all_results

async def pass_1_bouncer(job_text: str) -> BouncerDecision:
    return await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=BouncerDecision,
        max_retries=3,
        messages=[
            {"role": "system", "content": "You are a pragmatic technical recruiter. Reject ONLY jobs that explicitly require Senior, Staff, or Lead level experience (5+ years). Allow Entry-level, Junior, Mid-level (up to 4 years), and Internship roles."},
            {"role": "user", "content": f"Analyze this job snippet: {job_text}"}
        ]
    )

async def pass_2_analyst(job_title: str, job_text: str, resume: str) -> AnalystScore:
    return await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        response_model=AnalystScore,
        max_retries=3,
        messages=[
            {"role": "system", "content": "You are an elite career coach. Score the candidate's fit for this role out of 100. Be highly critical."},
            {"role": "user", "content": f"Resume:\n{resume}\n\nJob snippet:\n{job_title} - {job_text}"}
        ]
    )

async def send_discord_alert(job_title, job_url, score, pitch):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ ERROR: DISCORD_WEBHOOK_URL is empty in your .env file!")
        return

    # THE MAGIC LINK: Encodes the URL to pass directly to your Streamlit app
    encoded_url = urllib.parse.quote(job_url)
    magic_link = f"http://localhost:8501/?url={encoded_url}"

    message = {
        "content": f"🚨 **High-Match Job Alert!** (Score: {score}/100)",
        "embeds": [{
            "title": job_title,
            "url": job_url,
            "description": f"**Why you fit:** {pitch}\n\n[🚀 OPEN IN CONTROL ROOM]({magic_link})",
            "color": 65280 
        }]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=message) as response:
            if response.status == 204:
                print(f"✅ Alert delivered to Discord for {job_title}!")
            else:
                text = await response.text()
                print(f"❌ Discord blocked the alert! Error {response.status}: {text}")

async def run_sniper():
    resume_path = "data/master_resume.txt"
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
    else:
        resume_text = "Software engineer looking for Python roles."
    
    # Gather jobs from all sources!
    jobs = []
    jobs.extend(await get_jobs_from_api('python,junior'))
    jobs.extend(await source_hackernews())
    jobs.extend(await source_github())
    jobs.extend(await source_gmail())
    
    if not jobs:
        print("No jobs found today.")
        return

    print(f"🎯 Found {len(jobs)} potential leads. Sending to the Bouncer...")

    async def process_job(job):
        decision = await pass_1_bouncer(job['body'])
        if not decision.is_valid:
            print(f"🚫 Bouncer rejected '{job['title']}': {decision.reason}")
            return
            
        print(f"✅ Bouncer approved '{job['title']}'. Sending to Analyst...")
        analysis = await pass_2_analyst(job['title'], job['body'], resume_text)
        
        # Threshold set moderately to 40
        if analysis.score >= 40:
            print(f"🔥 MATCH FOUND! Score: {analysis.score}. Sending alert...")
            await send_discord_alert(job['title'], job['href'], analysis.score, analysis.pitch)
        else:
            print(f"📉 Analyst rejected '{job['title']}' (Score: {analysis.score})")

    # Run the analysis concurrently for all found jobs
    await asyncio.gather(*(process_job(job) for job in jobs))

if __name__ == "__main__":
    asyncio.run(run_sniper())