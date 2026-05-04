# Multi-Agent Research Assistant

A 4-component agentic AI system that researches companies for sales teams using live web search and episodic memory.

## Architecture

- **Planner agent** — decomposes query into sub-questions
- **Searcher agent** — fetches live results via Tavily API
- **Synthesizer agent** — writes cited report via Groq LLM
- **Memory layer** — ChromaDB vector store for past research

## Tech stack

Python · Groq (Llama 3.3 70B) · Tavily · ChromaDB · FastAPI · Uvicorn

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key

## Run

```bash
python -m uvicorn api:app --reload
```
