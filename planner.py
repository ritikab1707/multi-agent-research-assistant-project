# import os
# import json
# from groq import Groq
# from dotenv import load_dotenv

# load_dotenv()
# client = Groq()

# def plan_research(query: str) -> list[str]:
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {
#                 "role": "system",
#                 "content": """You are a research planner. Given a question, break it into 
#                 3-5 specific sub-questions that together would fully answer the question.
#                 Return ONLY a valid JSON array of strings. No explanation, no preamble.
#                 Example: ["sub-question 1", "sub-question 2", "sub-question 3"]"""
#             },
#             {
#                 "role": "user",
#                 "content": f"Break this into sub-questions: {query}"
#             }
#         ],
#         max_tokens=500
#     )
#     raw = response.choices[0].message.content.strip()
#     # Strip markdown code fences if model wraps output in ```json ... ```
#     if raw.startswith("```"):
#         raw = raw.split("```")[1]
#         if raw.startswith("json"):
#             raw = raw[4:]
#     return json.loads(raw.strip())

# if __name__ == "__main__":
#     questions = plan_research("What is the impact of AI on the job market?")
#     for i, q in enumerate(questions, 1):
#         print(f"{i}. {q}")

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

def parse_questions(raw: str) -> list[str]:
    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw.strip())
        if not isinstance(result, list):
            print("Error: Expected a list from planner")
            return []
        return result
    except json.JSONDecodeError as e:
        print(f"Error parsing planner output: {e}")
        print(f"Raw output was: {raw}")
        return []

def plan_research(query: str) -> list[str]:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a research planner for a sales intelligence tool.
                    Break the query into 3-5 specific, non-overlapping sub-questions
                    that build a complete picture of the prospect for a sales team.
                    Return ONLY a JSON array of strings. No explanation. No preamble.
                    Example: ["question 1", "question 2", "question 3"]"""
                },
                {
                    "role": "user",
                    "content": f"Break this into sub-questions: {query}"
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        raw = response.choices[0].message.content.strip()
        return parse_questions(raw)

    except Exception as e:
        print(f"Error calling Groq API in planner: {e}")
        return []

if __name__ == "__main__":
    questions = plan_research("Research Salesforce for my sales call")
    if questions:
        print(f"Generated {len(questions)} sub-questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
    else:
        print("Planner failed — check errors above")