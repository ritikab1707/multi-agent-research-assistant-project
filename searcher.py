import os
import requests
from dotenv import load_dotenv

load_dotenv()

def search(query: str) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")

    # Catch missing API key before even making the call
    if not api_key:
        print("Error: TAVILY_API_KEY not found in .env file")
        return []

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": 3,
                "include_raw_content": False
            },
            timeout=10  # Don't wait forever — fail after 10 seconds
        )

        # Layer 2: Check status code
        if response.status_code == 401:
            print("Error: Invalid Tavily API key. Check your .env file.")
            return []
        elif response.status_code == 429:
            print("Error: Tavily rate limit hit. Wait a moment and try again.")
            return []
        elif response.status_code >= 500:
            print(f"Error: Tavily server error ({response.status_code}). Try again later.")
            return []
        elif response.status_code != 200:
            print(f"Error: Unexpected status code {response.status_code}")
            return []

        # Layer 3: Parse response body safely
        data = response.json()
        results = data.get("results", [])

        # Safely extract only results that have all three fields
        clean_results = []
        for r in results:
            if all(key in r for key in ["title", "content", "url"]):
                clean_results.append({
                    "title": r["title"],
                    "content": r["content"],
                    "url": r["url"]
                })

        return clean_results

    # Layer 1: Network-level failures
    except requests.exceptions.ConnectionError:
        print("Error: No internet connection or Tavily is unreachable.")
        return []
    except requests.exceptions.Timeout:
        print("Error: Request timed out after 10 seconds.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error: Something went wrong with the request — {e}")
        return []

    # Layer 3: JSON parsing failure
    except ValueError:
        print("Error: Tavily returned invalid JSON.")
        return []


if __name__ == "__main__":
    results = search("How is AI affecting employment in manufacturing?")

    if not results:
        print("No results returned — check errors above.")
    else:
        for r in results:
            print(r["title"])
            print(r["content"][:200])
            print()