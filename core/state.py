from typing import TypedDict, Optional, List
from core.models import StructuredJob, CompanyIntel, ColdEmailDraft, SkillGapPlan, InterviewPlaybook, TailoredResume

class JobHunterState(TypedDict):
    # Inputs
    raw_job_url: str
    raw_job_html: str
    user_resume_context: str
    
    # Checkpoints
    structured_job: Optional[StructuredJob]
    company_intel: Optional[CompanyIntel]
    drafted_email: Optional[ColdEmailDraft]
    skill_gap_plan: Optional[SkillGapPlan]
    interview_playbook: Optional[InterviewPlaybook]
    tailored_resume: Optional[TailoredResume] # NEW: Stores the rewritten resume
    
    # System
    error_logs: List[str]