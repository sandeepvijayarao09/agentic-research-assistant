<div align="center">

# 🧠 Agentic Research Assistant

**Plan → Reason → Act**

A multi-agent LLM research system with persistent memory, tool use, and VLA-inspired coordination. Specialized agents for research and reasoning work together through an orchestrator to solve complex tasks.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

---

## 📋 Overview

This system implements the foundational **Plan→Reason→Act** loop from Vision-Language-Action (VLA) architectures, adapted for research automation. An orchestrator agent decomposes complex queries, routes tasks to specialized research and reasoning agents, and synthesizes results — all backed by dual-layer memory (ChromaDB long-term + sliding-window working memory).

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent Coordination** | Orchestrator routes to Research and Reasoning specialists |
| **Plan→Reason→Act Loop** | VLA-inspired task decomposition and execution |
| **Persistent Memory** | ChromaDB semantic search + working memory pruning |
| **Tool Registry** | OpenAI-compatible function calling (Calculator, ArXiv, Search) |
| **Async Support** | Full asyncio for concurrent agent operations |

---

## 🎬 Demo

<!-- Add demo screenshot or GIF here -->
<!-- ![Demo](assets/demo.gif) -->

> **📸 Demo placeholder** — Run `python main.py` to start the interactive CLI and try queries like *"What are recent breakthroughs in quantum computing?"*

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    User Interface (CLI)                    │
└────────────────────────┬─────────────────────────────────┘
                         ▼
         ┌───────────────────────────────┐
         │      OrchestratorAgent        │
         │  ┌─────────────────────────┐  │
         │  │  Plan → Reason → Act    │  │
         │  │  - Task Decomposition   │  │
         │  │  - Agent Routing        │  │
         │  │  - Result Synthesis     │  │
         │  └─────────────────────────┘  │
         └──────┬───────────────┬────────┘
                │               │
     ┌──────────▼──┐    ┌──────▼──────────┐
     │  Research   │    │   Reasoning     │
     │  Agent      │    │   Agent         │
     │             │    │                 │
     │  ArXiv      │    │  Chain-of-      │
     │  Search     │    │   Thought       │
     │  Citations  │    │  Hypotheses     │
     │  Summary    │    │  Fact-Check     │
     └──────┬──────┘    └──────┬──────────┘
            │                  │
     ┌──────▼──────────────────▼──────────┐
     │         Tool Registry              │
     │  Calculator / ArXiv / Web Search   │
     └──────────────┬─────────────────────┘
                    │
     ┌──────────────▼─────────────────────┐
     │        Memory Management           │
     │  ┌────────────┬─────────────────┐  │
     │  │ Long-Term  │ Working Memory  │  │
     │  │ (ChromaDB) │ (Sliding Window)│  │
     │  │ Semantic   │ Priority Prune  │  │
     │  │ Vectors    │ Token Mgmt     │  │
     │  └────────────┴─────────────────┘  │
     └────────────────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/sandeepvijayarao09/agentic-research-assistant.git
cd agentic-research-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API key
export OPENAI_API_KEY="sk-..."

# 4. Launch interactive CLI
python main.py
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Conduct research on a topic |
| `reason <task>` | Perform reasoning analysis |
| `stats` | Show memory and system statistics |
| `help` | Show available commands |
| `quit` | Exit |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Backend | GPT-4 / GPT-3.5 (OpenAI) |
| Agent Framework | LangChain |
| Vector Database | ChromaDB |
| Paper Search | ArXiv API |
| Function Calling | OpenAI-compatible JSON Schema |
| Testing | pytest with mocks |

---

## 🔬 Agent Details

### OrchestratorAgent
The master coordinator implementing Plan→Reason→Act:
- Decomposes complex queries into subtasks
- Routes to specialized agents (research, reasoning)
- Synthesizes multi-agent results
- Multi-iteration for complex problems

### ResearchAgent
Specialized for information gathering:
- ArXiv paper search with filtering
- Query expansion for broader results
- Citation extraction and formatting
- Source quality evaluation

### ReasoningAgent
Analysis and logical inference:
- Chain-of-thought with step decomposition
- Multi-hypothesis generation
- Comparative analysis
- Fact-checking with source verification

### Memory System

| Layer | Storage | Purpose |
|-------|---------|---------|
| **Long-Term** | ChromaDB vectors | Semantic search, session persistence |
| **Working** | Sliding window | Task-relevant context, token management |
| **Handoff** | Automatic | Working memory compresses to long-term |

---

<details>
<summary><b>📖 Configuration</b> (click to expand)</summary>

### LLM Settings
```python
self.llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=api_key,
)
```

### Memory Configuration
```python
self.long_term_memory = LongTermMemory(persist_dir=".memory")
self.working_memory = WorkingMemory(max_tokens=4000)
```

</details>

---

## 📁 Project Structure

```
agentic-research-assistant/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py      # Master coordinator
│   │   ├── research_agent.py    # Research specialist
│   │   └── reasoning_agent.py   # Analysis specialist
│   ├── memory/
│   │   ├── long_term_memory.py  # ChromaDB persistence
│   │   └── working_memory.py    # Context management
│   └── tools/
│       ├── tool_registry.py     # Function calling framework
│       ├── calculator.py        # Math operations
│       └── arxiv_search.py      # Paper retrieval
├── tests/
│   └── test_orchestrator.py     # Unit tests
├── main.py                       # Interactive CLI
├── requirements.txt
└── README.md
```

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Tests cover: planning phase, reasoning phase, action execution, end-to-end integration, error handling, and memory persistence.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
