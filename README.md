# Agentic Research Assistant - Multi-Agent LLM Pipeline

A production-quality multi-agent research system implementing the foundational Plan→Reason→Act loop from Vision-Language-Action (VLA) systems. This system coordinates specialized agents to conduct research, reasoning, and fact-checking tasks with persistent long-term memory and dynamic working memory management.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (CLI)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  OrchestratorAgent              │
        │  ┌──────────────────────────┐  │
        │  │ Plan→Reason→Act Loop     │  │
        │  │ - Task Decomposition     │  │
        │  │ - Agent Routing          │  │
        │  │ - Result Synthesis       │  │
        │  └──────────────────────────┘  │
        └────┬──────────────────────┬────┘
             │                      │
    ┌────────▼────┐      ┌─────────▼────────┐
    │ Research    │      │ Reasoning        │
    │ Agent       │      │ Agent            │
    │ - ArXiv     │      │ - Chain-of-Th.   │
    │ - Search    │      │ - Hypotheses     │
    │ - Citations │      │ - Analysis       │
    └────────┬────┘      └────────┬─────────┘
             │                     │
    ┌────────▼─────────────────────▼────────────┐
    │           Tool Registry & Tools           │
    │  ┌──────────────────────────────────────┐ │
    │  │ • Calculator                         │ │
    │  │ • Web Search                         │ │
    │  │ • DateTime                           │ │
    │  │ • Memory Recall                      │ │
    │  └──────────────────────────────────────┘ │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │         Memory Management Layer           │
    │ ┌──────────────┬──────────────────────┐  │
    │ │ Long-Term    │ Working Memory       │  │
    │ │ Memory       │ (Context Window)     │  │
    │ │              │                      │  │
    │ │ • ChromaDB   │ • Sliding Window     │  │
    │ │ • Semantic   │ • Priority Pruning   │  │
    │ │   Search     │ • Task Injection     │  │
    │ │ • Vectors    │ • Token Management   │  │
    │ └──────────────┴──────────────────────┘  │
    └──────────────────────────────────────────┘
```

## Core Components

### 1. OrchestratorAgent (`src/agents/orchestrator.py`)
Master agent implementing Plan→Reason→Act loop:
- Decomposes complex user queries into subtasks
- Routes tasks to specialized agents (research, reasoning)
- Synthesizes results across multiple agents
- Manages conversation history
- Coordinates multi-iteration execution for complex problems
- Agent registry and dynamic routing

### 2. ResearchAgent (`src/agents/research_agent.py`)
Specialized research conducting:
- ArXiv paper search and retrieval with filtering
- Query expansion to broader search terms
- Citation extraction and formatting
- Source quality evaluation
- Research session tracking and memory
- Paper summarization

### 3. ReasoningAgent (`src/agents/reasoning_agent.py`)
Analysis and logical inference specialist:
- Chain-of-thought reasoning with explicit step decomposition
- Multi-hypothesis generation and evaluation
- Comparative analysis across items and criteria
- Fact-checking with source verification
- Insight synthesis from multiple information pieces
- Problem decomposition and strategic reasoning

### 4. Memory Management

**Long-Term Memory (`src/memory/long_term_memory.py`)**
- ChromaDB vector database for semantic search
- Memory type categorization (research, reasoning, query, result)
- Importance scoring and usage frequency tracking
- Session-based organization
- Memory consolidation for old entries
- Persistent checkpoint save/load

**Working Memory (`src/memory/working_memory.py`)**
- Sliding window mechanism for recent items
- Priority-based memory pruning when capacity exceeded
- Token counting and context window management
- Task-relevant memory injection based on query
- Compression to long-term storage

### 5. Tool System (`src/tools/`)
- **Tool Registry**: OpenAI-compatible function calling framework
  - JSON Schema definitions for tool parameters
  - Async execution support
  - Error handling and logging
- **Calculator**: Math operations (add, subtract, multiply, divide, power, sqrt)
- **ArXiv Search**: Academic paper retrieval with filtering

## Key Features

1. **Multi-Agent Coordination**: Specialized agents for research and reasoning with intelligent routing
2. **Persistent Memory**: Long-term semantic memory with ChromaDB, working memory with intelligent pruning
3. **Plan→Reason→Act Loop**: Foundational VLA system pattern for solving complex tasks
4. **Function Calling**: Tool registry with OpenAI-compatible schemas
5. **Async Support**: Full asyncio support for concurrent operations
6. **Extensible Architecture**: Easy to add new agents, tools, and memory backends

## Installation

```bash
cd /path/to/agentic-research-assistant
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
```

## Usage

### Start Interactive CLI

```bash
python main.py
```

### Available Commands

```
search <query>  - Conduct research on a topic
reason <task>   - Perform reasoning analysis
stats          - Show memory and system statistics
help           - Show available commands
quit           - Exit the assistant
```

### Example Sessions

```
You: What are recent breakthroughs in quantum computing?
Assistant: Researching quantum computing...
Found 5 sources:
- Paper: "Quantum Error Correction Advances" by Smith et al.
  Summary: Recent work on scalable QEC...

Key Findings:
- Improved error correction rates
- New qubit stabilization techniques
- Demonstrations on 100+ qubit systems

---

You: Compare machine learning and deep learning
Assistant: Analyzing comparison...

Reasoning Steps:
1. Define machine learning and deep learning
2. Identify key differences
3. Evaluate strengths and weaknesses
4. Determine use case applications

Conclusion:
Machine learning is broader, includes various algorithms...
Deep learning uses neural networks with multiple layers...
```

## Project Structure

```
agentic-research-assistant/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py      # Master coordinator
│   │   ├── research_agent.py    # Research specialist
│   │   └── reasoning_agent.py   # Analysis specialist
│   ├── memory/
│   │   ├── long_term_memory.py  # ChromaDB-backed persistence
│   │   └── working_memory.py    # Context management
│   └── tools/
│       ├── tool_registry.py     # Function calling framework
│       ├── calculator.py        # Math operations
│       └── arxiv_search.py      # Paper retrieval
├── tests/
│   └── test_orchestrator.py     # Unit tests with mocks
├── main.py                       # Interactive CLI
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## Requirements

- Python 3.8+
- OpenAI API key (for GPT-3.5/GPT-4)
- Dependencies: langchain, chromadb, arxiv, duckduckgo-search

## Testing

```bash
pytest tests/ -v
```

Tests include:
- Planning phase unit tests
- Reasoning phase tests
- Action execution tests
- Full end-to-end integration tests
- Error handling tests
- Memory persistence tests

## Configuration

Customize in `main.py`:
```python
self.llm = ChatOpenAI(
    model="gpt-4",              # or gpt-3.5-turbo
    temperature=0.7,             # Control creativity
    api_key=api_key,
)
```

Memory configuration:
```python
self.long_term_memory = LongTermMemory(persist_dir=".memory")
self.working_memory = WorkingMemory(max_tokens=4000)
```

## Architecture Highlights

### Plan→Reason→Act Loop Implementation

1. **PLAN**: Query decomposition into subtasks and strategy
2. **REASON**: Chain-of-thought reasoning to validate approach
3. **ACT**: Execution through specialized agents
4. **ITERATE**: Multi-iteration for complex problems

### Memory Integration

- **Short-term**: Working memory holds task-relevant context
- **Long-term**: ChromaDB stores semantic knowledge
- **Handoff**: Working memory compresses to long-term after task completion
- **Retrieval**: Semantic search injects relevant memories during execution

## Performance Notes

- First run initializes ChromaDB (creates vector indexes)
- ArXiv searches may take 2-5 seconds
- LLM calls depend on network and OpenAI latency
- Token management prevents context window overflow

## Future Enhancements

- Multi-model support (Claude, Llama, etc.)
- Web search integration (DuckDuckGo API)
- Document ingestion and analysis
- Persistent conversation sessions
- Advanced memory consolidation with summarization
- Tool composition and chaining
- Parallel agent execution

## License

MIT

## Contributing

Contributions welcome! Areas for enhancement:
- Additional specialized agents
- More tool implementations
- Memory optimization
- Testing coverage
