from langgraph.graph import StateGraph, END
from core.state import JobHunterState
from agent.nodes import (
    scrape_job_node, 
    extract_jd_node, 
    retrieve_context_node,
    gather_intel_node, 
    draft_email_node, 
    generate_plan_node,
    prep_interview_node,
    tailor_resume_node # <-- Import the new node
)

def build_graph():
    workflow = StateGraph(JobHunterState)

    workflow.add_node("scrape_job", scrape_job_node)
    workflow.add_node("extract_jd", extract_jd_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("gather_intel", gather_intel_node)
    workflow.add_node("draft_email", draft_email_node)
    workflow.add_node("generate_plan", generate_plan_node)
    workflow.add_node("prep_interview", prep_interview_node)
    workflow.add_node("tailor_resume", tailor_resume_node) # <-- Add to graph

    workflow.set_entry_point("scrape_job")
    
    workflow.add_edge("scrape_job", "extract_jd")
    workflow.add_edge("extract_jd", "gather_intel")
    workflow.add_edge("extract_jd", "retrieve_context")
    
    # All branches run in parallel after context is retrieved
    workflow.add_edge("gather_intel", "draft_email")
    workflow.add_edge("retrieve_context", "draft_email")
    
    workflow.add_edge("gather_intel", "generate_plan")
    workflow.add_edge("retrieve_context", "generate_plan")

    workflow.add_edge("gather_intel", "prep_interview")
    workflow.add_edge("retrieve_context", "prep_interview")
    
    # New branch for rewriting the resume!
    workflow.add_edge("retrieve_context", "tailor_resume")
    
    workflow.add_edge("draft_email", END)
    workflow.add_edge("generate_plan", END)
    workflow.add_edge("prep_interview", END)
    workflow.add_edge("tailor_resume", END)

    return workflow.compile()

job_hunter_app = build_graph()