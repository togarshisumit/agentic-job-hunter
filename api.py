from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agent.workflow import job_hunter_app
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="Agentic Job Hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For the Chrome extension
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    url: str
    html: str
    company_name: str = ""

@app.post("/analyze_job")
async def analyze_job(req: JobRequest):
    initial_state = {
        "raw_job_url": req.url,
        "raw_job_html": f"Company: {req.company_name}\n\n{req.html}" if req.company_name else req.html,
        "user_resume_context": "", 
        "error_logs": []
    }
    
    # Run the LangGraph agent pipeline
    result = job_hunter_app.invoke(initial_state)
    
    # Serialize Pydantic models in the result dict for JSON response
    serialized_result = {}
    for key, val in result.items():
        if hasattr(val, "model_dump"):
            serialized_result[key] = val.model_dump()
        elif isinstance(val, list):
            serialized_result[key] = [v.model_dump() if hasattr(v, "model_dump") else v for v in val]
        else:
            serialized_result[key] = val
            
    return serialized_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
