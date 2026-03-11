# Agentic Research Assistant - Complete File Index

## Quick Start

1. **Installation**: `pip install -r requirements.txt`
2. **Setup**: `export OPENAI_API_KEY="sk-..."`
3. **Run**: `python main.py`
4. **Test**: `pytest tests/ -v`

## Documentation

| File | Purpose | Lines |
|------|---------|-------|
| [README.md](README.md) | User guide, usage examples, installation | 210 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Deep-dive architecture, data structures, patterns | 450 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Completion summary, features, code quality | 240 |
| [INDEX.md](INDEX.md) | This file - project navigation | - |

## Source Code

### Core Agents (`src/agents/`)
| File | Purpose | Lines | Classes |
|------|---------|-------|---------|
| [orchestrator.py](src/agents/orchestrator.py) | Master Plan→Reason→Act coordinator | 280 | 1 (OrchestratorAgent) |
| [research_agent.py](src/agents/research_agent.py) | Research specialist (papers, sources) | 250 | 1 (ResearchAgent) |
| [reasoning_agent.py](src/agents/reasoning_agent.py) | Analysis specialist (reasoning, hypotheses) | 310 | 1 (ReasoningAgent) |

**Total Agents**: 3 specialized agents
**Key Methods**: 25+ public methods across agents
**LLM Integration**: Full LangChain integration

### Memory Systems (`src/memory/`)
| File | Purpose | Lines | Classes |
|------|---------|-------|---------|
| [long_term_memory.py](src/memory/long_term_memory.py) | Persistent ChromaDB-backed memory | 290 | 2 (LongTermMemory, MemoryEntry) |
| [working_memory.py](src/memory/working_memory.py) | Context window management | 220 | 2 (WorkingMemory, MemoryItem) |

**Memory Types**: Research, Reasoning, Query, Result, General
**Search Methods**: Semantic search, keyword search, type-based, tag-based
**Storage**: ChromaDB vectors + in-memory dict + JSON checkpoints

### Tool System (`src/tools/`)
| File | Purpose | Lines | Classes |
|------|---------|-------|---------|
| [tool_registry.py](src/tools/tool_registry.py) | Function calling framework | 160 | 2 (Tool, ToolRegistry) |
| [calculator.py](src/tools/calculator.py) | Math operations | 85 | 1 (Calculator) |
| [arxiv_search.py](src/tools/arxiv_search.py) | Academic paper retrieval | 150 | 1 (ArxivSearch) |

**Built-in Tools**: 3 (calculator, get_current_time, recall_memory)
**Tool Schemas**: OpenAI-compatible JSON format
**Execution**: Async with error handling

## Entry Points

| File | Purpose | Type |
|------|---------|------|
| [main.py](main.py) | Interactive CLI interface | Entry point |
| [verify_project.py](verify_project.py) | Project verification & health check | Utility |

## Testing

| File | Purpose | Lines | Test Cases |
|------|---------|-------|------------|
| [test_orchestrator.py](tests/test_orchestrator.py) | Unit + integration tests | 370 | 15+ |

**Coverage**: Planning, Reasoning, Action, Integration, Memory, Routing
**Mocking**: Mock LLM calls for reproducibility
**Async**: Full pytest-asyncio support

## Configuration Files

| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python dependencies |
| [.gitignore](.gitignore) | Git exclusions |

## Directory Structure

```
agentic-research-assistant/
├── src/                          # Source code
│   ├── agents/                   # Agent implementations
│   │   ├── orchestrator.py
│   │   ├── research_agent.py
│   │   ├── reasoning_agent.py
│   │   └── __init__.py
│   ├── memory/                   # Memory systems
│   │   ├── long_term_memory.py
│   │   ├── working_memory.py
│   │   └── __init__.py
│   ├── tools/                    # Tool implementations
│   │   ├── tool_registry.py
│   │   ├── calculator.py
│   │   ├── arxiv_search.py
│   │   └── __init__.py
│   └── __init__.py
├── tests/                        # Test suite
│   ├── test_orchestrator.py
│   └── __init__.py
├── main.py                       # Interactive CLI
├── verify_project.py             # Verification utility
├── requirements.txt              # Dependencies
├── .gitignore                    # Git exclusions
├── README.md                     # User guide
├── ARCHITECTURE.md               # Architecture docs
├── PROJECT_SUMMARY.md            # Project summary
└── INDEX.md                      # This file
```

## Code Statistics

| Metric | Count |
|--------|-------|
| Total Python files | 15 |
| Total lines of code | 2,352 |
| Total documentation lines | 1,200+ |
| Source files | 12 |
| Test files | 1 |
| Classes | 15+ |
| Methods | 100+ |
| Async methods | 20+ |

## Key Components Overview

### 1. OrchestratorAgent
- Implements Plan→Reason→Act loop
- Routes tasks to specialized agents
- Manages conversation history
- Coordinates multi-iteration execution
- Methods: 12 public methods

### 2. ResearchAgent
- ArXiv paper search and retrieval
- Query expansion
- Citation extraction
- Source quality evaluation
- Methods: 8 public methods

### 3. ReasoningAgent
- Chain-of-thought reasoning
- Hypothesis generation
- Comparative analysis
- Fact-checking
- Insight synthesis
- Methods: 7 public methods

### 4. Long-Term Memory
- ChromaDB vector storage
- Semantic search
- Type-based categorization
- Importance scoring
- Memory consolidation
- Methods: 12 public methods

### 5. Working Memory
- Sliding window management
- Priority-based pruning
- Token counting
- Task-relevant injection
- Methods: 9 public methods

### 6. Tool Registry
- OpenAI-compatible schemas
- Async execution
- Error handling
- Extensible registration
- Methods: 8 public methods

## Dependencies

**Core LLM**:
- langchain (0.1.8)
- langchain-community (0.0.24)
- langchain-openai (0.0.5)
- openai (1.3.5)

**Memory**:
- chromadb (0.4.22)

**Research Tools**:
- arxiv (1.4.7)
- duckduckgo-search (3.9.10)

**Utilities**:
- pydantic (2.5.0)
- python-dotenv (1.0.0)
- aiohttp (3.9.1)

**Testing**:
- pytest (7.4.3)
- pytest-asyncio (0.21.1)

## How to Use This Project

### For Users
1. Read [README.md](README.md) for installation and usage
2. Run `python main.py` for interactive CLI
3. Follow example commands in README

### For Developers
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design patterns
2. Examine [src/agents/orchestrator.py](src/agents/orchestrator.py) for main loop
3. Check [tests/test_orchestrator.py](tests/test_orchestrator.py) for examples
4. Extend with new agents/tools following patterns

### For Contributors
1. Follow the agent pattern in [src/agents/research_agent.py](src/agents/research_agent.py)
2. Use [src/tools/tool_registry.py](src/tools/tool_registry.py) for new tools
3. Add tests in [tests/test_orchestrator.py](tests/test_orchestrator.py)
4. Update documentation

## File Locations

Base path: `/sessions/hopeful-cool-pascal/projects/agentic-research-assistant/`

All paths in this index are relative to the base directory.

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set API key: `export OPENAI_API_KEY="sk-..."`
3. Verify: `python verify_project.py`
4. Run: `python main.py`
5. Test: `pytest tests/ -v`

## Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [ArXiv API Documentation](https://arxiv.org/help/api/)
