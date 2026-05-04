import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

def synthesize(original_query: str, search_results: list[dict]) -> str:
    
    # Guard clause — if no results came in, return early
    if not search_results:
        return "No search results were found to synthesize a report from."

    results_text = "\n\n".join([
        f"Source [{i+1}]: {r['url']}\n{r['content']}"
        for i, r in enumerate(search_results)
    ])

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a senior sales intelligence analyst.
                    Given search results about a prospect company, write a concise
                    research report for a sales rep preparing for a call.
                    
                    Structure your report as:
                    1. A 2-sentence summary at the top
                    2. Key findings written in prose — no bullet points
                    3. Citations as [1], [2] etc. linked only to sources provided
                    
                    Only use information present in the search results.
                    Never invent facts or URLs not given to you."""
                },
                {
                    "role": "user",
                    "content": f"Query: {original_query}\n\nSearch results:\n{results_text}"
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error calling Groq API in synthesizer: {e}")
        return "Synthesis failed — check errors above."


if __name__ == "__main__":
    # Test with sample data so you can run this file independently
    sample_results = [
        {
            "title": "Salesforce Q3 2024 Earnings",
            "content": "Salesforce reported $9.4 billion in revenue for Q3 2024, a 11% increase year over year. The company highlighted strong growth in its AI product Einstein.",
            "url": "https://example.com/salesforce-q3"
        },
        {
            "title": "Salesforce Competitors 2024",
            "content": "Salesforce faces increasing competition from Microsoft Dynamics, HubSpot, and emerging AI-native CRMs. Customers cite high pricing as a key pain point.",
            "url": "https://example.com/salesforce-competitors"
        }
    ]
    report = synthesize("Research Salesforce for my sales call", sample_results)
    print(report)