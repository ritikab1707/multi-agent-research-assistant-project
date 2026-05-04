import os
import chromadb
from chromadb.utils import embedding_functions

# Set up ChromaDB — stores data locally in a folder called "agent_memory"
client = chromadb.PersistentClient(path="agent_memory")

# Use a simple sentence transformer for embeddings — no API key needed
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# Create (or load if it already exists) a collection for research reports
collection = client.get_or_create_collection(
    name="research_reports",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)


def save_research(query: str, report: str) -> None:
    """Save a research report to memory, keyed by the query."""
    try:
        collection.upsert(
            documents=[report],      # The full report text
            metadatas=[{"query": query}],  # The original query as metadata
            ids=[_make_id(query)]    # Unique ID based on query
        )
        print(f"Memory: Report saved for '{query}'")
    except Exception as e:
        print(f"Memory: Failed to save report — {e}")


def find_similar_research(query: str, threshold: float = 0.5) -> str | None:
    """
    Check if we've already researched something similar.
    Returns the stored report if similarity is above threshold, else None.
    threshold: 0.0 = accept anything, 1.0 = exact match only
    0.85 is a good balance — catches 'Research Salesforce' and 'Salesforce sales call'
    as the same topic.
    """
    try:
        # Need at least one item in collection before querying
        if collection.count() == 0:
            return None

        results = collection.query(
            query_texts=[query],
            n_results=1  # Only fetch the closest match
        )

        if not results["documents"] or not results["documents"][0]:
            return None

        # ChromaDB returns distances — lower = more similar
        # Convert to similarity score: similarity = 1 - distance
        distance = results["distances"][0][0]
        similarity = 1 - distance
        # print(f"Memory debug: distance={distance:.4f}, similarity={similarity:.4f}")

        if similarity >= threshold:
            matched_query = results["metadatas"][0][0]["query"]
            print(f"Memory: Found similar past research (similarity: {similarity:.2f})")
            print(f"Memory: Matched to previous query — '{matched_query}'")
            return results["documents"][0][0]  # Return the stored report

        return None  # Not similar enough — run fresh research

    except Exception as e:
        print(f"Memory: Query failed — {e}")
        return None


def list_past_research() -> list[str]:
    """List all queries that have been researched and stored."""
    try:
        all_items = collection.get()
        return [m["query"] for m in all_items["metadatas"]]
    except Exception as e:
        print(f"Memory: Could not list past research — {e}")
        return []


def _make_id(query: str) -> str:
    """Create a clean ID from a query string."""
    return query.lower().strip().replace(" ", "_")[:100]


if __name__ == "__main__":
    # Test memory independently
    print("Testing memory layer...\n")

    # Save a fake report
    save_research(
        "Research Salesforce for my sales call",
        "Salesforce is a leading CRM platform with $9.4B revenue..."
    )

    # Try to find it with a similar query
    result = find_similar_research("Tell me about Salesforce")
    if result:
        print(f"\nFound stored report:\n{result[:200]}...")
    else:
        print("\nNo similar research found")

    # List everything stored
    print(f"\nAll past research: {list_past_research()}")