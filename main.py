from planner import plan_research
from searcher import search
from synthesizer import synthesize
from memory import save_research, find_similar_research, list_past_research


def run_research_agent(query: str) -> tuple[str, list[str]]:
    print(f"\n{'='*50}")
    print(f"Research query: {query}")
    print(f"{'='*50}\n")

    print("Step 0: Checking memory for past research...")
    cached_report = find_similar_research(query)

    if cached_report:
        print("Memory hit — returning stored report instantly\n")
        return cached_report, []

    print("No similar research found — running full pipeline\n")

    print("Step 1: Planning research...")
    sub_questions = plan_research(query)

    if not sub_questions:
        return "Planning failed — could not generate sub-questions.", []

    print(f"Generated {len(sub_questions)} sub-questions:")
    for i, q in enumerate(sub_questions, 1):
        print(f"  {i}. {q}")

    print("\nStep 2: Searching for each sub-question...")
    all_results = []

    for i, question in enumerate(sub_questions, 1):
        print(f"  Searching ({i}/{len(sub_questions)}): {question[:60]}...")
        results = search(question)

        if results:
            all_results.extend(results)
            print(f"  Found {len(results)} results")
        else:
            print(f"  No results found — continuing")

    if not all_results:
        return "Search failed — no results found.", []

    print(f"\nTotal results collected: {len(all_results)}")

    print("\nStep 3: Synthesizing report...")
    report = synthesize(query, all_results)

    print("\nStep 4: Saving to memory...")
    save_research(query, report)

    return report, sub_questions   # ← return both


if __name__ == "__main__":
    past = list_past_research()
    if past:
        print(f"Past research in memory: {past}\n")

    query = "Research Salesforce for my sales call"
    report, sub_questions = run_research_agent(query)

    print(f"\n{'='*50}")
    print("SUB-QUESTIONS")
    print(f"{'='*50}")
    for i, q in enumerate(sub_questions, 1):
        print(f"{i}. {q}")

    print(f"\n{'='*50}")
    print("FINAL REPORT")
    print(f"{'='*50}\n")
    print(report)