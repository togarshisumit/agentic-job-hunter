import streamlit as st
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv

load_dotenv()
from agent.workflow import job_hunter_app
from agent.gmail_service import create_gmail_draft
from agent.auto_applier import apply_to_job

st.set_page_config(page_title="Agentic Job Hunter", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Font */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
            padding-top: 2rem;
        }
        
        /* Main background */
        .stApp {
            background-color: #020617;
            color: #f8fafc;
        }

        /* Gradient Text */
        .gradient-text {
            background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 3rem;
            padding-bottom: 0.5rem;
            margin-bottom: 0px;
        }
        
        /* Subtitle */
        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-top: -10px;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Cards */
        .css-1r6slb0, .css-12oz5g7 {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            backdrop-filter: blur(12px);
            margin-bottom: 1rem;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.39);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.5);
            border: none;
            color: white;
        }
        
        /* Secondary Buttons */
        .stButton > button[kind="secondary"] {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid #334155;
            box-shadow: none;
        }
        .stButton > button[kind="secondary"]:hover {
            background: rgba(51, 65, 85, 0.8);
            border: 1px solid #475569;
        }
        
        /* Inputs */
        .stTextInput > div > div > input, .stTextArea > div > textarea {
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid #334155 !important;
            color: #f8fafc !important;
            border-radius: 10px !important;
            padding: 0.75rem !important;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {
            border-color: #8b5cf6 !important;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: transparent;
            padding-bottom: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(30, 41, 59, 0.5);
            border-radius: 10px;
            padding: 10px 20px;
            border: 1px solid transparent;
            color: #94a3b8;
            font-weight: 500;
            transition: all 0.2s;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc;
            background-color: rgba(51, 65, 85, 0.8);
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(139, 92, 246, 0.15) !important;
            border: 1px solid rgba(139, 92, 246, 0.5) !important;
            color: #c4b5fd !important;
        }
        
        /* Alerts */
        .stAlert {
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Radio Buttons */
        .stRadio > div {
            background: rgba(30, 41, 59, 0.3);
            padding: 10px;
            border-radius: 10px;
        }
        
        /* Dataframes */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #334155;
        }
        </style>
    """, unsafe_allow_html=True)

DB_FILE = "job_tracker.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Company TEXT,
            Role TEXT,
            "Missing Skills" TEXT,
            "Email Drafted" TEXT,
            Status TEXT
        )
    ''')
    return conn

def save_to_db(job_title, company, missing_skills, email_subject):
    conn = get_db_connection()
    new_data = pd.DataFrame([{
        "Company": company,
        "Role": job_title,
        "Missing Skills": ", ".join(missing_skills),
        "Email Drafted": email_subject,
        "Status": "Ready to Apply"
    }])
    new_data.to_sql("jobs", conn, if_exists="append", index=False)
    conn.close()
    return True

def main():
    inject_custom_css()
    
    st.markdown('<h1 class="gradient-text">🎯 Agentic Job Hunter</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your AI-powered command center for autonomous job hunting, application, and tracking.</p>', unsafe_allow_html=True)
    
    query_params = st.query_params
    magic_url = query_params.get("url", "")

    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #fff;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**System Connections**")
        # Fix for the Streamlit magic bug (it evaluates expressions and prints them)
        if os.getenv("GROQ_API_KEY"):
            st.success("✅ Groq API Connected")
        else:
            st.error("❌ Groq API Missing")
            
        if os.getenv("LANGCHAIN_TRACING_V2") == "true":
            st.success("✅ LangSmith Tracing Active")
        else:
            st.warning("⚠️ LangSmith Disabled")
        
        st.markdown("---")
        view_mode = st.radio("Navigation", ["🤖 Agent Workspace", "⚙️ Settings"])

    if "agent_result" not in st.session_state:
        st.session_state.agent_result = None

    # Step 1: Input Section
    st.markdown("### 📥 1. Ingest Job Description")
    
    default_input = 0 if magic_url else 1
    input_method = st.radio("Choose Input Method:", ["🌐 Paste Job URL", "📝 Manual Text/HTML"], index=default_input, horizontal=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if input_method == "🌐 Paste Job URL":
            job_url = st.text_input("Job Link", value=magic_url, placeholder="https://careers.company.com/job/123", label_visibility="collapsed")
            job_html = ""
        else:
            job_url = "N/A"
            job_html = st.text_area("Paste Job HTML or Text here", height=150, label_visibility="collapsed", placeholder="Paste JD here...")
            
        company_name = st.text_input("Target Company Name", placeholder="e.g., SpaceX (Optional)")
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_button = st.button("🚀 Run AI Pipeline", use_container_width=True, type="primary")

    if run_button and (job_html or job_url):
        with st.spinner("🧠 Agent is scraping, analyzing, and strategizing..."):
            initial_state = {
                "raw_job_url": job_url,
                "raw_job_html": f"Company: {company_name}\n\n" + job_html if company_name else job_html,
                "user_resume_context": "", 
                "error_logs": []
            }
            try:
                st.session_state.agent_result = job_hunter_app.invoke(initial_state)
                st.toast("Pipeline Complete! Intelligence Report generated.", icon="✅")
            except Exception as e:
                st.error(f"Agent Pipeline Failed: {str(e)}")

    if st.session_state.agent_result:
        result = st.session_state.agent_result
        st.markdown("<br><hr style='border-color: #334155;'><br>", unsafe_allow_html=True)
        st.markdown("### 📊 Intelligence Report")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🧩 JD Analyst", "📄 Tailored Resume", "✉️ Action Center", "📈 7-Day Plan", "🎙️ Shadow Interviewer", "🗂️ Database"])
        
        with tab1:
            job = result.get("structured_job")
            if job:
                st.markdown(f"#### Role: <span style='color: #8b5cf6;'>{job.role_title}</span> @ {job.company_name}", unsafe_allow_html=True)
                st.table([{"Skill Required": req.skill, "Experience Level": req.level, "Dealbreaker?": "🚨 YES" if req.is_dealbreaker else "✅ Nice-to-have"} for req in job.core_skills])

        with tab2:
            resume = result.get("tailored_resume")
            if resume:
                st.success("**Professional Summary:**\n\n" + resume.professional_summary)
                st.markdown("#### Top Achievements Tailored for this Role:")
                for bullet in resume.tailored_bullets:
                    st.markdown(f"- {bullet}")

        with tab3:
            email = result.get("drafted_email")
            if email:
                st.markdown(f"#### ✉️ Crafted Cold Email")
                st.info(f"**Subject:** {email.subject_line}")
                email_body = st.text_area("Email Body (Editable):", value=email.body, height=200, label_visibility="collapsed")
                
                colA, colB = st.columns(2)
                with colA:
                    target_email = st.text_input("Target Email Address:", placeholder="hiring.manager@company.com")
                    if st.button("📧 Save to Gmail Drafts", type="primary", use_container_width=True):
                        if not target_email:
                            st.warning("Please enter a target email address first!")
                        else:
                            with st.spinner("Connecting to Gmail API..."):
                                status = create_gmail_draft(target_email, email.subject_line, email_body)
                                if "✅" in status:
                                    st.success(status)
                                else:
                                    st.error(status)
                
                st.markdown("<br><hr style='border-color: #334155;'><br>", unsafe_allow_html=True)
                st.markdown("#### 🤖 The Auto-Applier")
                st.caption("Let the Playwright bot autonomously navigate and fill out the application on your behalf.")
                
                colX, colY = st.columns(2)
                with colX:
                    resume_pdf_path = st.text_input("Path to your Base Resume PDF:", value="data/documents/Sumit Togarshi Resume.pdf")
                    if st.button("🚀 Launch Invisible Auto-Applier", type="secondary", use_container_width=True):
                        if job_url and "http" in job_url:
                            with st.spinner("Firing up Playwright engine..."):
                                applier_status = apply_to_job(job_url, resume_pdf_path)
                                st.info(applier_status)
                        else:
                            st.warning("You must provide a valid Job URL at the top to use the Auto-Applier.")

        with tab4:
            plan = result.get("skill_gap_plan")
            if plan:
                st.warning(f"**Missing Skills Detected:** {', '.join(plan.missing_skills)}")
                st.markdown("#### Your Custom 7-Day Upskilling Plan")
                for day, task in enumerate(plan.daily_plan, 1):
                    st.checkbox(f"**Day {day}:** {task}")
                    
        with tab5:
            playbook = result.get("interview_playbook")
            if playbook:
                colA, colB = st.columns(2)
                with colA:
                    st.error("💻 **Predicted Technical Questions:**")
                    for q in playbook.technical_questions: st.markdown(f"- {q}")
                with colB:
                    st.warning("🤝 **Predicted Behavioral Questions:**")
                    for q in playbook.behavioral_questions: st.markdown(f"- {q}")

        with tab6:
            st.markdown("#### Database Records")
            colA, _ = st.columns([1, 2])
            with colA:
                if st.button("💾 Save Job to Database", type="primary", use_container_width=True):
                    job = result.get("structured_job")
                    if save_to_db(job.role_title, job.company_name, result.get("skill_gap_plan").missing_skills, result.get("drafted_email").subject_line):
                        st.success(f"Saved to {DB_FILE} successfully!")
            
            if os.path.exists(DB_FILE):
                st.markdown("<br>", unsafe_allow_html=True)
                conn = get_db_connection()
                st.dataframe(pd.read_sql("SELECT * FROM jobs ORDER BY id DESC", conn), use_container_width=True)
                conn.close()

if __name__ == "__main__":
    main()