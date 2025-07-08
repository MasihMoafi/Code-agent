# Code-Agent: An Autonomous "Code as Action" Agent

This project is a lightweight, powerful implementation of the "Code Agent" paradigm, inspired by the "smol-developer" concept. Instead of relying on pre-defined tools, the AI agent generates its own plan and logic as a complete, executable Python script to accomplish a given task.

The system is composed of specialized agents that think and act entirely in code, orchestrated by a supervisor to solve complex problems autonomously.

## The "Code as Action" Paradigm

The core philosophy of this project is that the agent's thoughts, plans, and actions are all expressed as code. The workflow is as follows:

1.  **Prompting:** The agent is given a high-level task.
2.  **Code Generation:** The LLM generates a self-contained Python script designed to solve that task. This script *is* the agent's plan.
3.  **Execution:** The generated script is executed in a sandboxed environment.
4.  **Output:** The result of the script's execution (its `stdout`) is captured as the final output.

This approach provides maximum flexibility and power, as the agent is not limited by a fixed set of tools.

## Agent Architecture

The system uses a supervisor to manage a team of specialized agents:

-   **`ResearchAgent`:** Given a topic, this agent generates and executes a Python script to research the topic and prints its findings.
-   **`CodeAgent`:** Given a programming task and research context, this agent generates and executes a Python script to produce the final, functional code.

## Features

-   **Code as Action:** Agents generate and execute their own Python scripts to perform tasks.
-   **Autonomous Orchestration:** A supervisor agent manages the workflow between research and coding.
-   **Local First:** Powered by `ollama`, allowing you to run powerful models like Qwen and Gemma locally for privacy and control.
-   **Minimalist & Powerful:** A lightweight framework demonstrating a sophisticated agentic development paradigm.

## Technologies Used

-   **LLM Service:** `ollama`
-   **Language:** Python

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MasihMoafi/Code-agent.git
    cd Code-agent
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Ollama:**
    -   Ensure `ollama` is installed and running.
    -   Pull the model used by the agents (e.g., Qwen):
        ```bash
        ollama pull qwen
        ```

## Usage

Run the supervisor assistant with your high-level goal. The supervisor will orchestrate the research and coding agents to produce the final script.

```bash
python s_assist.py "Create a classic snake game using pygame."
```

The final generated code will be saved to a file, and the process will be logged to the console.
