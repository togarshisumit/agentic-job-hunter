from typing import List, Optional
from pydantic import BaseModel, Field

class JobRequirement(BaseModel):
    skill: str = Field(..., description="Specific technical or soft skill mentioned.")
    level: str = Field(..., description="Required level, e.g., 'expert', '3+ years', or 'familiar'.")
    is_dealbreaker: bool = Field(..., description="True if listed as a hard requirement, False if a 'nice to have'.")

class StructuredJob(BaseModel):
    role_title: str = Field(..., description="The standardized job title.")
    company_name: str = Field(..., description="Name of the hiring company.")
    core_skills: List[JobRequirement] = Field(..., description="List of required and preferred skills.")
    salary_range: Optional[str] = Field(None, description="Extracted salary range, if present.")
    culture_flags: List[str] = Field(..., description="Clues about work culture.")

class CompanyIntel(BaseModel):
    recent_news: List[str] = Field(..., description="Top 3 recent news events or product launches.")
    tech_stack_clues: List[str] = Field(..., description="Technologies mentioned in engineering blogs.")
    market_position: str = Field(..., description="Brief summary of their core product and market.")

class ColdEmailDraft(BaseModel):
    subject_line: str = Field(..., description="Catchy, non-spammy subject line under 8 words.")
    body: str = Field(..., description="The email body. Must mention a specific company detail and map it to user's past project.")
    rationale: str = Field(..., description="Internal reasoning for why this email will convert.")

class SkillGapPlan(BaseModel):
    missing_skills: List[str] = Field(..., description="Skills the user lacks based on their resume.")
    daily_plan: List[str] = Field(..., description="Exactly 7 strings, detailing the daily learning objectives.")

class InterviewPlaybook(BaseModel):
    technical_questions: List[str] = Field(..., description="Top 3 highly specific technical questions they will likely ask based on the JD and company tech stack.")
    behavioral_questions: List[str] = Field(..., description="Top 2 behavioral questions based on the company's recent news and culture.")
    positioning_strategy: str = Field(..., description="A 2-sentence strategy on how the candidate should pitch themselves to overcome their missing skills.")

# --- NEW: ATS Resume Tailor ---
class TailoredResume(BaseModel):
    professional_summary: str = Field(..., description="A 3-sentence summary tailored exactly to the job description keywords.")
    tailored_bullets: List[str] = Field(..., description="5 bullet points rewritten from the user's past projects to highlight skills the job requires. NEVER invent experience, just rephrase existing experience.")