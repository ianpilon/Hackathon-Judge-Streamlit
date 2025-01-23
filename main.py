from crewai_tools import YoutubeVideoSearchTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize the tool with Ollama configuration
    tool = YoutubeVideoSearchTool(
        config=dict(
            llm=dict(
                provider="ollama",
                config=dict(
                    model="llama2",
                    temperature=0.5,
                ),
            ),
            embedder=dict(
                provider="ollama",
                config=dict(
                    model="llama2",
                ),
            ),
        )
    )
    
    # Example search query
    search_query = "What are the main features of CrewAI?"
    
    try:
        # Perform the search
        result = tool.run(search_query)
        print("\nSearch Results:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
