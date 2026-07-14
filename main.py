import os
from dotenv import load_dotenv

# 1. LOAD THE API KEY FIRST before importing any agent code!
load_dotenv()

# 2. NOW WE CAN IMPORT THE AGENT
from agent.workflow import job_hunter_app

def run_agent():
    # Mock data to test the pipeline locally
    initial_state = {
        "raw_job_url": "https://careers.stripe.com/job/123",
        "raw_job_html": """
            <h1>Senior Backend Engineer</h1>
            <p>We are looking for a backend engineer with 5+ years of Python and FastAPI experience.</p>
            <p>Nice to have: Kubernetes and AWS.</p>
        """,
        "user_resume_context": "I am a software engineer with 3 years of experience in Node.js and React. I have touched Docker but no AWS.",
        "error_logs": []
    }
    
    print("🚀 Firing up the LangGraph Job Hunter Agent...")
    
    # .invoke() runs the graph from start to finish
    result_state = job_hunter_app.invoke(initial_state)
    
    print("\n✅ --- JOB PARSED ---")
    print(result_state["structured_job"])
    
    print("\n✅ --- DRAFTED EMAIL ---")
    if result_state.get("drafted_email"):
        print(result_state["drafted_email"].body)
        print(f"\nRationale: {result_state['drafted_email'].rationale}")
    
    print("\n✅ --- 7-DAY UPSKILL PLAN ---")
    if result_state.get("skill_gap_plan"):
        for day, task in enumerate(result_state["skill_gap_plan"].daily_plan, 1):
            print(f"Day {day}: {task}")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY is missing from your .env file or environment.")
        print("Did Windows accidentally name your file '.env.txt'?")
    else:
        run_agent()