# System Design Document: Kasparro AI Agentic Content Generation System

## 1. System Overview
The **Kasparro AI Agentic Content Generation System** is an advanced, generative framework designed to autonomously create high-quality e-commerce content. Unlike simple template-based scripts, this system utilizes a **Self-Correcting Directed Acyclic Graph (DAG)** of cognitive agents powered by **Google Gemini**.

The system takes unstructured, raw product text as input and employs a shared state machine to orchestrate complex tasks:
1.  **Thinking:** Inventing realistic competitor products based on market context.
2.  **Reasoning:** Generating context-aware FAQ answers (e.g., specific dermatological advice).
3.  **Reflecting:** Critiquing its own work and autonomously retrying if quality standards aren't met.
4.  **Verifying:** Grounding AI hallucinations with deterministic logic tools.

## 2. Architecture (LangGraph DAG)

The system is built on **LangGraph**, utilizing a StateGraph architecture where a shared memory object (`AgentState`) is passed between specialized nodes.

The architecture features a **Cyclic Feedback Loop**: If the QA node rejects the output, the graph loops back to the Strategist node to regenerate content.

```mermaid
classDiagram
    class AgentState {
        +RawInput str
        +Product product
        +Competitor competitor
        +List~Question~ questions
        +str critique
        +int retry_count
    }

    class Product {
        +str name
        +float price
        +List~str~ ingredients
    }

    class Competitor {
        +str reason_for_creation
    }

    %% Relationships
    AgentState *-- Product
    AgentState *-- Competitor
    Product <|-- Competitor : Inherits
```

## 3. Core Components

### 3.1 Agents (Graph Nodes)
Agents are the autonomous nodes in the graph, each responsible for a specific cognitive or functional task. They are defined in `src/agents.py`.

| Agent Node | Type | Responsibility | Key Logic |
| :--- | :--- | :--- | :--- |
| **Ingestion Agent** | **LLM Extraction** | Cleans messy text into strict `Product` objects. | Uses Pydantic extraction with Gemini to parse unstructured text into a validated schema. |
| **Strategist Agent** | **LLM Creative** | Invents content and responds to feedback. | Uses high-temperature LLM calls to **hallucinate** competitors. Reads `state.critique` to adjust strategy on retries. |
| **QA & Critic Agent** | **Quality Gate** | Validates content quality and compliance. | Checks if FAQ count >= 15. Uses a separate LLM call to grade relevance. Triggers retry loops if constraints fail. |
| **Logic Engine** | **Deterministic Tool** | Grounds the AI with math and facts. | Calls pure Python functions (`calculate_price_delta`) to verify the AI's "Better Value" claims mathematically. |
| **Assembly Agent** | **Formatter** | Compiles the final state into output files. | Aggregates the accumulated state and renders it into the final 3 JSON formats. |

### 3.2 Logic Tools ("Muscles")
Reusable, deterministic utility functions that verify or transform data. Defined in `src/logic_tools.py`.

* **`calculate_price_delta(p1, p2)`**:
    * *Role:* Computes the exact price difference between the Product and the AI-generated Competitor.
    * *Output:* Returns metrics like `diff`, `is_cheaper`, and `percent_diff`.
* **`extract_ingredient_overlap(list1, list2)`**:
    * *Role:* Performs set operations to find common vs. unique ingredients.
    * *Output:* Used to generate the "Advantage Summary" in the comparison page.

### 3.3 Data Models (Schema)
The system uses **Pydantic** models to enforce strict types and ensure the LLM outputs machine-readable JSON. Defined in `src/models.py`.

* **`Product`**:
    * Fields: `name`, `price`, `currency`, `concentration`, `skin_type`, `ingredients`, `benefits`, `how_to_use`, `side_effects`.
* **`Competitor` (Inherits Product)**:
    * Adds: `reason_for_creation` (Why the AI chose this specific competitor strategy).
* **`AgentState`**:
    * The "Brain" of the graph. It holds the `raw_input`, `product` object, `competitor` object, and `questions` list.
    * **New Fields:** `critique` (feedback from QA) and `retry_count` (loop safety).

## 4. Directory Structure
The project follows a flat, modular structure optimized for LLM agent workflows.

```text
src/
├── agents.py       # The "Nodes" of the graph (Ingestion, Strategist, QA, etc.)
├── logic_tools.py  # The "Tools" (Math, Set operations)
├── models.py       # The "Schema" (Pydantic models)
├── __init__.py
tests/
├── test_system.py  # Unit tests for logic and constraints
```

## 5. Technology Stack
- **Orchestration**: LangGraph
- **LLM**: Google Gemini 2.5 Pro (via `langchain-google-genai`)
- **Validation**: Pydantic (Data integrity)
- **Language**: Python 3.10+