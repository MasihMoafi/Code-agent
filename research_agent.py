import os
import traceback
import re
import json
import httpx
from bs4 import BeautifulSoup
from smolagents import CodeAgent, tool, LiteLLMModel

# --- Configuration ---
LLM_MODEL = 'qwen3:8b'
MEMORY_FILE = 'memory.txt'

# --- Proxy Clearing Function ---
def clear_proxy_settings():
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        if var in os.environ:
            del os.environ[var]

clear_proxy_settings()

# --- Agent Tools ---
@tool
def web_search(query: str) -> str:
    """
    Searches the web for information using DuckDuckGo.
    Args:
        query: The search query.
    """
    print(f"Tool: web_search, Query: {query}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        with httpx.Client(headers=headers, follow_redirects=True, timeout=15) as client:
            response = client.get("https://duckduckgo.com/html/", params={"q": query})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            snippets = [div.get_text(strip=True) for div in soup.select('a.result__snippet')[:5]]
            return "\n".join(snippets) if snippets else "No search results found."
    except Exception as e:
        return f"Error during web search: {e}"

@tool
def save_to_memory(fact: str) -> str:
    """
    Saves a new, important fact to the long-term memory file.
    Args:
        fact: The string containing the fact to be remembered.
    """
    print(f"Tool: save_to_memory, Fact: {fact}")
    try:
        with open(MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(fact + "\n")
        return "Fact saved to memory successfully."
    except Exception as e:
        return f"Error saving to memory: {e}"

# --- Main Execution ---
def main():
    print("--- Initializing Learning Researcher Agent ---")

    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            f.write("--- Research Memory ---\n")
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        long_term_memory = f.read()

    # --- THE FIX IS IN THIS PROMPT ---
    system_prompt = """
    You are a Research Assistant. Your goal is to answer the user's questions accurately.
    You have access to a long-term memory and a set of tools.

    **Your instructions are:**
    1.  **Consult Memory First:** Review the `long_term_memory` argument. If the answer is there, provide it directly using the `final_answer` tool.
    2.  **Search if Necessary:** If the information is not in your memory, use the `web_search` tool to find it.
    3.  **Save New Knowledge:** When you discover a new, critical fact, you MUST save it by calling the `save_to_memory` tool.
    4.  **Deliver the Final Answer:** Once your research is complete, you MUST call the `final_answer()` tool with your complete summary as the argument. Example: `print(final_answer("The capital of France is Paris."))`

    You must use `print(tool_name(arguments))` to call your tools.
    """

    try:
        model = LiteLLMModel(
            model_id=f"ollama/{LLM_MODEL}",
            api_key="ollama"
        )
        print(f"Successfully initialized LiteLLMModel for Ollama model: {LLM_MODEL}")

        agent = CodeAgent(
            model=model,
            tools=[web_search, save_to_memory]
        )
        print("CodeAgent created successfully.")
        
        user_question = input("\nWhat would you like to research? ")

        if user_question:
            print("\n--- Agent is thinking... ---")
            final_answer = agent.run(
                task=user_question,
                additional_args={"long_term_memory": long_term_memory}
            )
            print("\n--- Final Answer from Agent ---")
            print(final_answer)

    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()