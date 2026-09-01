import argparse
import sys
from dotenv import load_dotenv
from src.graph import app

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Self-Corrective RAG Agent")
    parser.add_argument(
        "--query", 
        type=str, 
        default="How do telemetry thresholds detect anomalies?",
        help="Query string for the agent"
    )
    args = parser.parse_args()

    print(f"\n[?] Input Query: {args.query}")
    initial_state = {"question": args.query, "iterations": 0}
    
    try:
        result = app.invoke(initial_state)
        print("\n[+] Final Generated Answer:")
        print(result.get("generation"))
    except Exception as e:
        print(f"\n[!] Execution error (Ensure OPENAI_API_KEY is exported): {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
