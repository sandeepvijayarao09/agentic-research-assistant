"""Unit tests for the Orchestrator Agent with mocked LLM calls"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage

from src.agents.orchestrator import OrchestratorAgent
from src.memory.long_term_memory import LongTermMemory
from src.memory.working_memory import WorkingMemory
from src.tools.tool_registry import ToolRegistry


@pytest.fixture
def mock_llm():
    """Create a mock LLM"""
    llm = Mock(spec=ChatOpenAI)
    return llm


@pytest.fixture
def memory_system():
    """Create memory systems for testing"""
    long_term = LongTermMemory()
    working = WorkingMemory()
    return long_term, working


@pytest.fixture
def tool_registry():
    """Create tool registry"""
    return ToolRegistry()


@pytest.fixture
def orchestrator(mock_llm, memory_system, tool_registry):
    """Create orchestrator with mocked components"""
    long_term, working = memory_system
    return OrchestratorAgent(mock_llm, long_term, working, tool_registry)


class TestOrchestratorPlanning:
    """Test the Planning phase"""

    @pytest.mark.asyncio
    async def test_plan_generation(self, orchestrator, mock_llm):
        """Test that plan is generated correctly"""
        # Mock LLM response
        plan_json = """{
            "strategy": "Search for information and analyze it",
            "subtasks": ["research", "analyze"],
            "agents_needed": ["research", "reasoning"]
        }"""
        mock_llm.invoke.return_value = AIMessage(content=plan_json)

        plan = await orchestrator._plan("What is machine learning?", 1, [])

        assert "strategy" in plan
        assert "subtasks" in plan
        assert "agents_needed" in plan
        mock_llm.invoke.assert_called()

    @pytest.mark.asyncio
    async def test_plan_with_previous_iterations(self, orchestrator, mock_llm):
        """Test planning considers previous iterations"""
        plan_json = """{
            "strategy": "Refine based on previous results",
            "subtasks": ["deeper_analysis"],
            "agents_needed": ["reasoning"]
        }"""
        mock_llm.invoke.return_value = AIMessage(content=plan_json)

        previous = [
            {
                "iteration": 1,
                "action_result": {"observation": "Found some initial results"}
            }
        ]

        plan = await orchestrator._plan("What is ML?", 2, previous)
        assert plan is not None


class TestOrchestratorReasoning:
    """Test the Reasoning phase"""

    @pytest.mark.asyncio
    async def test_reasoning_execution(self, orchestrator):
        """Test reasoning phase execution"""
        plan = {
            "strategy": "Think through the problem",
            "subtasks": ["analyze"],
        }

        # Mock the reasoning agent
        with patch.object(
            orchestrator.reasoning_agent,
            "chain_of_thought",
            new_callable=AsyncMock,
        ) as mock_cot:
            mock_cot.return_value = {
                "problem": "test",
                "reasoning": "Step 1: Analyze the problem",
                "steps": ["Step 1", "Step 2"],
            }

            result = await orchestrator._reason(plan, "test query")

            assert result is not None
            assert "chain_of_thought" in result
            assert "next_actions" in result


class TestOrchestratorAction:
    """Test the Action phase"""

    @pytest.mark.asyncio
    async def test_action_execution(self, orchestrator):
        """Test action phase with mocked agents"""
        plan = {
            "strategy": "Conduct research",
            "subtasks": ["research"],
            "agents_needed": ["research"],
        }
        reasoning = {"chain_of_thought": "Analyze", "next_actions": ["research"]}

        with patch.object(
            orchestrator.research_agent,
            "conduct_research",
            new_callable=AsyncMock,
        ) as mock_research:
            mock_research.return_value = {
                "query": "test",
                "sources": [{"title": "Test Paper", "url": "http://test.com"}],
                "findings": ["Finding 1"],
            }

            result = await orchestrator._act(plan, reasoning)

            assert result is not None
            assert "observations" in result
            assert result["complete"] is True


class TestOrchestratorIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_full_task_execution(self, orchestrator):
        """Test full task execution loop"""
        with patch.object(
            orchestrator.reasoning_agent,
            "chain_of_thought",
            new_callable=AsyncMock,
        ) as mock_cot, \
        patch.object(
            orchestrator.research_agent,
            "conduct_research",
            new_callable=AsyncMock,
        ) as mock_research, \
        patch.object(
            orchestrator,
            "_plan",
            new_callable=AsyncMock,
        ) as mock_plan:

            # Setup mocks
            mock_plan.return_value = {
                "strategy": "Test",
                "subtasks": ["research"],
                "agents_needed": ["research"],
            }

            mock_research.return_value = {
                "query": "test",
                "sources": [{"title": "Test"}],
                "findings": ["Finding 1"],
            }

            mock_cot.return_value = {
                "reasoning": "Analyzed",
                "steps": ["Step 1"],
            }

            result = await orchestrator.execute_task("What is AI?", max_iterations=1)

            assert result is not None
            assert "query" in result
            assert "iterations" in result
            assert len(result["iterations"]) > 0

    @pytest.mark.asyncio
    async def test_conversation_history(self, orchestrator):
        """Test conversation history tracking"""
        orchestrator.add_to_conversation("user", "What is ML?")
        orchestrator.add_to_conversation("assistant", "Machine learning is...")

        history = orchestrator.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_agent_routing(self, orchestrator):
        """Test task routing to agents"""
        with patch.object(
            orchestrator.research_agent,
            "conduct_research",
            new_callable=AsyncMock,
        ) as mock_research:

            mock_research.return_value = {"sources": [], "findings": []}

            result = await orchestrator.route_task("AI research", "research")
            assert result is not None

    @pytest.mark.asyncio
    async def test_tool_execution(self, orchestrator):
        """Test tool execution through orchestrator"""
        result = await orchestrator.execute_tool("get_current_time")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_execution_summary(self, orchestrator):
        """Test execution summary generation"""
        summary = orchestrator.get_execution_summary()

        assert "tasks_completed" in summary
        assert "conversation_turns" in summary
        assert "agents_available" in summary
        assert "tools_available" in summary


class TestOrchestratorMemory:
    """Test memory integration"""

    @pytest.mark.asyncio
    async def test_memory_persistence(self, orchestrator):
        """Test that tasks are stored in memory"""
        with patch.object(
            orchestrator.reasoning_agent,
            "chain_of_thought",
            new_callable=AsyncMock,
        ) as mock_cot, \
        patch.object(
            orchestrator,
            "_plan",
            new_callable=AsyncMock,
        ) as mock_plan, \
        patch.object(
            orchestrator,
            "_act",
            new_callable=AsyncMock,
        ) as mock_act:

            mock_plan.return_value = {
                "strategy": "Test",
                "subtasks": [],
                "agents_needed": [],
            }

            mock_cot.return_value = {"reasoning": "Test"}

            mock_act.return_value = {
                "complete": True,
                "answer": "Test answer",
                "observations": [],
                "agent_outputs": {},
            }

            await orchestrator.execute_task("Test task", max_iterations=1)

            # Check memory
            stats = orchestrator.memory.get_memory_stats()
            assert stats["total_memories"] > 0

    def test_working_memory_integration(self, orchestrator):
        """Test working memory is updated"""
        initial_items = len(orchestrator.working_memory.items)

        orchestrator.working_memory.add_item("Test item", priority=0.8)

        assert len(orchestrator.working_memory.items) == initial_items + 1


class TestOrchestratorErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_invalid_agent_routing(self, orchestrator):
        """Test routing to non-existent agent"""
        result = await orchestrator.route_task("Test task", "nonexistent_agent")
        assert result is None

    @pytest.mark.asyncio
    async def test_malformed_plan_handling(self, orchestrator, mock_llm):
        """Test handling of malformed plan JSON"""
        mock_llm.invoke.return_value = AIMessage(content="Not valid JSON")

        plan = await orchestrator._plan("Test", 1, [])
        # Should still return a valid plan structure
        assert isinstance(plan, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
