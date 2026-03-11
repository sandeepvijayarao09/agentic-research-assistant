#!/usr/bin/env python3
"""
Verification script for the Agentic Research Assistant project.
Checks that all components are properly installed and importable.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_imports():
    """Verify all modules can be imported"""
    print("Verifying imports...")
    errors = []

    try:
        from src.agents.orchestrator import OrchestratorAgent
        print("✓ OrchestratorAgent imported")
    except Exception as e:
        errors.append(f"OrchestratorAgent: {e}")

    try:
        from src.agents.research_agent import ResearchAgent
        print("✓ ResearchAgent imported")
    except Exception as e:
        errors.append(f"ResearchAgent: {e}")

    try:
        from src.agents.reasoning_agent import ReasoningAgent
        print("✓ ReasoningAgent imported")
    except Exception as e:
        errors.append(f"ReasoningAgent: {e}")

    try:
        from src.memory.long_term_memory import LongTermMemory
        print("✓ LongTermMemory imported")
    except Exception as e:
        errors.append(f"LongTermMemory: {e}")

    try:
        from src.memory.working_memory import WorkingMemory
        print("✓ WorkingMemory imported")
    except Exception as e:
        errors.append(f"WorkingMemory: {e}")

    try:
        from src.tools.tool_registry import ToolRegistry
        print("✓ ToolRegistry imported")
    except Exception as e:
        errors.append(f"ToolRegistry: {e}")

    try:
        from src.tools.calculator import Calculator
        print("✓ Calculator imported")
    except Exception as e:
        errors.append(f"Calculator: {e}")

    try:
        from src.tools.arxiv_search import ArxivSearch
        print("✓ ArxivSearch imported")
    except Exception as e:
        errors.append(f"ArxivSearch: {e}")

    return errors


def verify_file_structure():
    """Verify all expected files exist"""
    print("\nVerifying file structure...")
    base_path = Path(__file__).parent
    expected_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "src/__init__.py",
        "src/agents/__init__.py",
        "src/agents/orchestrator.py",
        "src/agents/research_agent.py",
        "src/agents/reasoning_agent.py",
        "src/memory/__init__.py",
        "src/memory/long_term_memory.py",
        "src/memory/working_memory.py",
        "src/tools/__init__.py",
        "src/tools/tool_registry.py",
        "src/tools/calculator.py",
        "src/tools/arxiv_search.py",
        "tests/__init__.py",
        "tests/test_orchestrator.py",
    ]

    errors = []
    for file_path in expected_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            errors.append(f"Missing: {file_path}")

    return errors


def verify_tool_registry():
    """Verify tool registry functionality"""
    print("\nVerifying Tool Registry...")
    errors = []

    try:
        from src.tools.tool_registry import ToolRegistry

        registry = ToolRegistry()

        # Check built-in tools
        tools = registry.list_tools()
        expected_tools = ["calculator", "get_current_time", "recall_memory"]

        for tool in expected_tools:
            if tool in tools:
                print(f"✓ Tool registered: {tool}")
            else:
                errors.append(f"Missing tool: {tool}")

        # Check schemas
        schemas = registry.get_schemas()
        if len(schemas) > 0:
            print(f"✓ Tool schemas generated: {len(schemas)} tools")
        else:
            errors.append("No tool schemas generated")

    except Exception as e:
        errors.append(f"Tool registry verification failed: {e}")

    return errors


def verify_memory_systems():
    """Verify memory systems"""
    print("\nVerifying Memory Systems...")
    errors = []

    try:
        from src.memory.long_term_memory import LongTermMemory

        memory = LongTermMemory()
        memory_id = memory.add_memory(
            "Test memory entry",
            memory_type="test",
            tags=["verification"],
        )
        print(f"✓ Long-term memory add: {memory_id}")

        # Search
        results = memory.search_semantic("test", limit=5)
        if len(results) > 0:
            print(f"✓ Semantic search works: {len(results)} results")
        else:
            print("⚠ Semantic search returned no results (ChromaDB may not be available)")

        stats = memory.get_memory_stats()
        print(f"✓ Memory stats: {stats['total_memories']} entries")

    except Exception as e:
        errors.append(f"Long-term memory verification failed: {e}")

    try:
        from src.memory.working_memory import WorkingMemory

        working = WorkingMemory(max_tokens=2000)
        working.add_item("Test item", priority=0.8)
        print("✓ Working memory add")

        summary = working.get_summary()
        print(f"✓ Working memory summary: {summary['items_count']} items")

    except Exception as e:
        errors.append(f"Working memory verification failed: {e}")

    return errors


def main():
    """Run all verifications"""
    print("=" * 60)
    print("Agentic Research Assistant - Project Verification")
    print("=" * 60)

    all_errors = []

    # Run verifications
    all_errors.extend(verify_file_structure())
    all_errors.extend(verify_imports())
    all_errors.extend(verify_tool_registry())
    all_errors.extend(verify_memory_systems())

    # Report results
    print("\n" + "=" * 60)
    if all_errors:
        print("VERIFICATION FAILED - Issues found:")
        print("=" * 60)
        for error in all_errors:
            print(f"✗ {error}")
        return 1
    else:
        print("VERIFICATION SUCCESSFUL - All components ready!")
        print("=" * 60)
        print("\nTo get started:")
        print("1. pip install -r requirements.txt")
        print("2. export OPENAI_API_KEY='sk-...'")
        print("3. python main.py")
        return 0


if __name__ == "__main__":
    sys.exit(main())
