# Agentic Research Assistant - Architecture Documentation

## Overview

The Agentic Research Assistant is a sophisticated multi-agent system implementing the Plan→Reason→Act loop pattern foundational to Vision-Language-Action (VLA) systems. The architecture enables autonomous task decomposition, multi-agent coordination, and persistent knowledge management.

## System Components

### 1. Orchestrator Agent (`src/agents/orchestrator.py`)

**Purpose**: Master coordinator that implements the Plan→Reason→Act loop

**Key Methods**:
- `execute_task(query, max_iterations)`: Main entry point for task execution
- `_plan(query, iteration, previous)`: Decompose query into strategy and subtasks
- `_reason(plan, query)`: Apply chain-of-thought reasoning to validate plan
- `_act(plan, reasoning)`: Execute planned actions through agents
- `route_task(task, agent_name)`: Route specific tasks to specialized agents

**Data Flow**:
```
User Query
    ↓
_plan() → Strategy + Subtasks
    ↓
_reason() → Validated approach
    ↓
_act() → Agent execution
    ↓
Synthesize results
    ↓
Check completion → Loop or Return
```

**Agent Registry**:
- `research`: ResearchAgent for information gathering
- `reasoning`: ReasoningAgent for analysis

### 2. Research Agent (`src/agents/research_agent.py`)

**Purpose**: Specialized information gathering and academic research

**Key Methods**:
- `conduct_research(query, depth)`: Execute research with specified depth
- `plan_research(query)`: Create research strategy and expand search terms
- `_synthesize_findings(query, sources)`: Extract key insights from sources
- `expand_query(query)`: Generate related search terms
- `extract_citations(sources)`: Format sources as citations
- `evaluate_source_quality(source)`: Score source credibility

**Capabilities**:
- ArXiv paper search (academic research)
- Query expansion for broader coverage
- Citation extraction and formatting
- Source quality evaluation
- Research session memory management

**Memory Integration**:
- Stores research plans in long-term memory
- Saves found papers and findings
- Tags memories with query terms for easy retrieval

### 3. Reasoning Agent (`src/agents/reasoning_agent.py`)

**Purpose**: Logical analysis and inference

**Key Methods**:
- `chain_of_thought(problem, context)`: Step-by-step reasoning with explicit steps
- `generate_hypotheses(scenario, num_hypotheses)`: Create and evaluate alternatives
- `comparative_analysis(items, criteria)`: Compare multiple items on criteria
- `fact_check(claims, sources)`: Verify claims against sources
- `synthesize_insights(information, theme)`: Extract patterns and insights

**Capabilities**:
- Explicit reasoning step decomposition
- Multi-hypothesis generation
- Structured comparative analysis
- Fact verification
- Cross-information synthesis

**Memory Integration**:
- Stores reasoning chains for future reference
- Tags hypotheses and analyses
- Tracks fact-check results

### 4. Long-Term Memory (`src/memory/long_term_memory.py`)

**Purpose**: Persistent semantic knowledge store

**Architecture**:
```
MemoryEntry
├── content (string)
├── memory_type (research|reasoning|query|result|general)
├── tags (list)
├── importance (0.0-1.0)
├── use_count (int)
└── timestamps (created_at, accessed_at)

LongTermMemory
├── In-memory dict (fast access)
└── ChromaDB collection (semantic search)
```

**Key Methods**:
- `add_memory(content, memory_type, tags, importance)`: Store new memory
- `search_semantic(query, limit)`: Vector similarity search
- `search_by_type(memory_type, limit)`: Filter by category
- `search_by_tags(tags, limit)`: Tag-based retrieval
- `update_importance(entry_id, importance)`: Update relevance score
- `consolidate_memories(days)`: Compress old memories

**Search Strategy**:
1. Try ChromaDB semantic search (if available)
2. Fall back to keyword search
3. Rank by importance and recency

**Memory Types**:
- **research**: Papers, sources, findings
- **reasoning**: Analysis, hypotheses, conclusions
- **query**: User questions and decomposed subtasks
- **result**: Intermediate and final results
- **general**: Session notes and observations

### 5. Working Memory (`src/memory/working_memory.py`)

**Purpose**: Context window management with intelligent pruning

**Architecture**:
```
WorkingMemory (max_tokens = 4000)
├── items (MemoryItem list)
│   ├── content (string)
│   ├── priority (0.0-1.0)
│   ├── token_count (int)
│   ├── created_at (datetime)
│   └── relevance_score (float)
└── total_tokens (int)
```

**Key Methods**:
- `add_item(content, priority, token_count)`: Add to working memory
- `get_context(task_relevant_query)`: Retrieve formatted context
- `_prune_to_fit(required_tokens)`: Make room by removing low-priority items
- `update_item_priority(index, priority)`: Adjust importance
- `compress_to_summary(max_tokens)`: Handoff to long-term memory

**Pruning Strategy**:
1. Protect most recent window_size items
2. Sort remaining by priority
3. Remove lowest-priority until space freed
4. Never lose task-relevant information

**Relevance Scoring**:
- Keyword matching: 0.9 if matches task query
- Semantic similarity: partial score for related items
- Recency: older items decrease in relevance

### 6. Tool Registry (`src/tools/tool_registry.py`)

**Purpose**: Unified function calling framework

**Architecture**:
```
Tool
├── name (string)
├── func (callable)
├── description (string)
├── parameters (dict)
├── required (list)
└── to_schema() → OpenAI-compatible format

ToolRegistry
├── tools (dict of Tool)
├── get_schemas() → LLM function calling format
├── execute_tool(name, **kwargs) → async execution
└── list_tools() → available tools
```

**Built-in Tools**:
1. **calculator**: Add, subtract, multiply, divide, power, sqrt
   - Parameters: operation, x, y
   - Type: synchronous

2. **get_current_time**: Current date and time
   - Parameters: (none)
   - Returns: ISO format timestamp

3. **recall_memory**: Query long-term memory
   - Parameters: query, limit
   - Returns: Matching memories

**Tool Schema Format** (OpenAI compatible):
```json
{
  "type": "function",
  "function": {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "parameters": {
      "type": "object",
      "properties": {
        "operation": {"type": "string"},
        "x": {"type": "number"},
        "y": {"type": "number"}
      },
      "required": ["operation", "x", "y"]
    }
  }
}
```

### 7. Supporting Tools

#### Calculator (`src/tools/calculator.py`)
- Basic arithmetic (add, subtract, multiply, divide, power)
- Advanced: sqrt, percentage
- Safe expression evaluation
- Last result tracking

#### ArXiv Search (`src/tools/arxiv_search.py`)
- Paper search with relevance ranking
- Author search filtering
- Category filtering
- Recent paper discovery
- Citation extraction
- Paper detail retrieval

## Data Structures

### MemoryEntry (LongTermMemory)
```python
@dataclass
class MemoryEntry:
    id: str (UUID)
    content: str
    memory_type: str
    session_id: str
    tags: List[str]
    created_at: datetime
    accessed_at: datetime
    importance: float (0.0-1.0)
    use_count: int
```

### MemoryItem (WorkingMemory)
```python
@dataclass
class MemoryItem:
    content: str
    priority: float (0.0-1.0)
    token_count: int
    created_at: datetime
    relevance_score: float
```

### ExecutionResult (Orchestrator)
```python
{
    "query": str,
    "started_at": ISO datetime,
    "iterations": [{
        "iteration": int,
        "plan": dict,
        "reasoning": dict,
        "action_result": dict,
        "timestamp": ISO datetime
    }],
    "final_answer": str,
    "sources_used": list,
    "completed_at": ISO datetime
}
```

## Execution Flow

### Complete Task Execution

```
User Input
    ↓
Orchestrator.execute_task()
    ├─ Working Memory: Add user query (priority=1.0)
    │
    └─ Loop (max iterations):
        │
        ├─ PLAN Phase:
        │   └─ Query decomposition → Strategy, subtasks, agents
        │
        ├─ REASON Phase:
        │   └─ Chain-of-thought on plan
        │
        ├─ ACT Phase:
        │   ├─ Research Agent (if needed):
        │   │   ├─ Query expansion
        │   │   ├─ ArXiv search
        │   │   ├─ Synthesis
        │   │   └─ Store findings in long-term memory
        │   │
        │   └─ Reasoning Agent (if needed):
        │       ├─ Chain-of-thought
        │       ├─ Hypothesis generation
        │       ├─ Analysis
        │       └─ Store reasoning in long-term memory
        │
        ├─ Check completion
        │
        └─ If not complete, loop
            (with previous iteration context)

Final: Store task completion in memory
       Compress working memory to long-term
       Return results to user
```

## Memory Lifecycle

```
1. CAPTURE:
   - Agents add memories as they work
   - Working memory accumulates context
   - Both tagged and timestamped

2. ACTIVE USE:
   - Working memory provides context to LLM
   - Semantic search retrieves relevant long-term memories
   - Importance scores updated by task relevance

3. PERSISTENCE:
   - Long-term memory backed by ChromaDB vectors
   - File checkpoints available
   - Session organization for multi-turn

4. CONSOLIDATION:
   - Identify old, low-use memories
   - Summarize before archiving
   - Compress to summaries
   - Space optimization
```

## Async Execution

All agent methods support async/await:
```python
# Parallel agent execution possible
async def _act(self, plan, reasoning):
    tasks = [
        orchestrator.research_agent.conduct_research(task)
        if "research" in task,
        orchestrator.reasoning_agent.chain_of_thought(task)
        if "reason" in task,
    ]
    results = await asyncio.gather(*tasks)
```

## Error Handling

**Tool Execution**:
- Wrap in try/except
- Return error string to LLM
- Log to file

**Agent Errors**:
- Graceful degradation
- Fallback to simpler approach
- Continue to next iteration

**Memory Errors**:
- ChromaDB unavailable → Use keyword search
- File I/O → Log and continue
- Token overflow → Aggressive pruning

## Extension Points

### Adding New Agent
```python
class MyAgent:
    def __init__(self, llm, memory, working_memory):
        self.llm = llm
        self.memory = memory
        self.working_memory = working_memory

    async def execute(self, task):
        # Implement logic
        self.memory.add_memory(result)
        return result

# Register in Orchestrator
self.agents["my_agent"] = MyAgent(...)
```

### Adding New Tool
```python
def my_tool(param1: str, param2: int) -> str:
    return f"Result: {param1} {param2}"

tool_registry.register(
    name="my_tool",
    func=my_tool,
    description="Does something useful",
    parameters={
        "param1": {"type": "string"},
        "param2": {"type": "integer"}
    },
    required=["param1", "param2"]
)
```

### Custom Memory Backend
Extend `LongTermMemory` and override `search_semantic()` to use different vector DB (Pinecone, Weaviate, etc.).

## Performance Considerations

1. **Token Management**: Working memory limited to 4000 tokens to preserve context
2. **Semantic Search**: First ChromaDB query may be slow (indexing), subsequent faster
3. **Agent Parallelization**: Future: run multiple agents in parallel with asyncio.gather()
4. **Memory Consolidation**: Run periodically to compress old memories
5. **Batch Operations**: Add multiple memories at once

## Security Notes

- Tool execution sandboxed (calculator uses safe eval)
- No file system access from tools
- All LLM inputs logged
- Memory checkpoint encryption optional
- No credentials stored in memory
