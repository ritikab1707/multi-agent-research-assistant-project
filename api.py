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

# --- Request and Response models ---

class ResearchRequest(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    query: str
    report: str
    source: str  # "memory" or "live_research"


# --- Endpoints ---

@app.get("/")
def root():
    """Health check — confirms the API is running."""
    return {"status": "running", "message": "Multi-Agent Research Assistant is live"}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    """
    Main endpoint. Takes a research query and returns a report.
    Checks memory first — runs full pipeline if no match found.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Check memory before running pipeline
        cached = find_similar_research(request.query)

        if cached:
            return ResearchResponse(
                query=request.query,
                report=cached,
                source="memory"
            )

        # Run full pipeline
        report = run_research_agent(request.query)

        if report.startswith("Planning failed") or report.startswith("Search failed"):
            raise HTTPException(status_code=500, detail=report)

        return ResearchResponse(
            query=request.query,
            report=report,
            source="live_research"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/memory")
def get_memory():
    """Returns all past research queries stored in memory."""
    past = list_past_research()
    return {
        "total": len(past),
        "past_queries": past
    }


@app.delete("/memory")
def clear_memory():
    """Clears all stored research from memory."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path="agent_memory")
        client.delete_collection("research_reports")
        return {"status": "Memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")