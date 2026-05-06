from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import run_research_agent
from memory import list_past_research, find_similar_research, save_research

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="A 4-component agentic system that researches companies for sales teams.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    sub_questions: list[str]   # ← new
    report: str
    source: str


@app.get("/")
def root():
    return {"status": "running", "message": "Multi-Agent Research Assistant is live"}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        cached = find_similar_research(request.query)

        if cached:
            return ResearchResponse(
                query=request.query,
                sub_questions=[],   # memory hits skip planning
                report=cached,
                source="memory"
            )

        report, sub_questions = run_research_agent(request.query)

        if report.startswith("Planning failed") or report.startswith("Search failed"):
            raise HTTPException(status_code=500, detail=report)

        return ResearchResponse(
            query=request.query,
            sub_questions=sub_questions,
            report=report,
            source="live_research"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/memory")
def get_memory():
    past = list_past_research()
    return {"total": len(past), "past_queries": past}


@app.delete("/memory")
def clear_memory():
    try:
        import chromadb
        client = chromadb.PersistentClient(path="agent_memory")
        client.delete_collection("research_reports")
        return {"status": "Memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")