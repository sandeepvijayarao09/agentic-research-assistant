"""Orchestrator Agent - Master agent coordinating Plan→Reason→Act loop"""

import logging
import json
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import asyncio

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from src.memory.long_term_memory import LongTermMemory
from src.memory.working_memory import WorkingMemory
from src.tools.tool_registry import ToolRegistry
from src.agents.research_agent import ResearchAgent
from src.agents.reasoning_agent import ReasoningAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Master orchestrator implementing Plan→Reason→Act loop.
    Coordinates between specialized agents and manages overall task execution.
    """

    def __init__(
        self,
        llm: ChatOpenAI,
        memory: LongTermMemory,
        working_memory: WorkingMemory,
        tool_registry: ToolRegistry,
    ):
        self.llm = llm
        self.memory = memory
        self.working_memory = working_memory
        self.tool_registry = tool_registry
        self.name = "OrchestratorAgent"

        # Initialize sub-agents
        self.research_agent = ResearchAgent(llm, memory, working_memory)
        self.reasoning_agent = ReasoningAgent(llm, memory, working_memory)

        # Registry of agents
        self.agents = {
            "research": self.research_agent,
            "reasoning": self.reasoning_agent,
        }

        self.conversation_history = []
        self.task_queue = []
        self.completed_tasks = []

    async def execute_task(self, user_query: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute a task using Plan→Reason→Act loop

        Args:
            user_query: User's request
            max_iterations: Maximum planning/reasoning/action iterations

        Returns:
            Task result with all steps documented
        """
        logger.info(f"Executing task: {user_query}")

        task_result = {
            "query": user_query,
            "started_at": datetime.now().isoformat(),
            "iterations": [],
            "final_answer": "",
            "sources_used": [],
        }

        # Add to working memory
        self.working_memory.add_item(
            f"User query: {user_query}",
            priority=1.0,
            token_count=50,
        )

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")

            # PLAN phase
            plan = await self._plan(user_query, iteration, task_result["iterations"])
            logger.info(f"Plan: {plan}")

            # REASON phase
            reasoning = await self._reason(plan, user_query)
            logger.info(f"Reasoning: {reasoning}")

            # ACT phase
            action_result = await self._act(plan, reasoning)
            logger.info(f"Action result: {action_result}")

            # Store iteration
            iteration_data = {
                "iteration": iteration,
                "plan": plan,
                "reasoning": reasoning,
                "action_result": action_result,
                "timestamp": datetime.now().isoformat(),
            }
            task_result["iterations"].append(iteration_data)

            # Check if task is complete
            if action_result.get("complete", False):
                task_result["final_answer"] = action_result.get("answer", "")
                break

        # Store task in memory
        self.memory.add_memory(
            f"Completed task: {user_query}. Answer: {task_result['final_answer'][:200]}",
            memory_type="general",
            tags=["task", "completed"],
        )

        task_result["completed_at"] = datetime.now().isoformat()
        self.completed_tasks.append(task_result)

        return task_result

    async def _plan(
        self, query: str, iteration: int, previous_iterations: List[Dict]
    ) -> Dict[str, Any]:
        """
        PLAN phase: Determine task decomposition and strategy

        Returns:
            Plan dictionary with approach and subtasks
        """
        system_prompt = """You are a strategic planner. Analyze the user query and create an action plan.
        Consider:
        1. What information is needed?
        2. What agents/tools should be used?
        3. In what order should tasks be executed?
        4. How to validate the answer?

        Return JSON with 'strategy', 'subtasks' (list), and 'agents_needed' (list)."""

        # Include context from previous iterations
        history_context = ""
        if previous_iterations:
            history_context = f"\nPrevious iterations: {len(previous_iterations)}\n"
            for prev in previous_iterations[-2:]:  # Last 2 iterations
                history_context += f"- Iteration {prev['iteration']}: {prev['action_result'].get('observation', '')[:100]}\n"

        prompt = f"Query: {query}{history_context}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ]

        response = self.llm.invoke(messages)

        try:
            plan = json.loads(response.content)
        except json.JSONDecodeError:
            plan = {
                "strategy": response.content,
                "subtasks": ["analyze", "research", "synthesize"],
                "agents_needed": ["research", "reasoning"],
            }

        return plan

    async def _reason(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        REASON phase: Apply reasoning to plan

        Returns:
            Reasoning steps and decisions
        """
        reasoning_result = await self.reasoning_agent.chain_of_thought(
            problem=f"How to execute plan: {plan.get('strategy', '')}",
            context=f"User query: {query}",
        )

        return {
            "chain_of_thought": reasoning_result,
            "next_actions": plan.get("subtasks", []),
            "validation_needed": True,
        }

    async def _act(
        self, plan: Dict[str, Any], reasoning: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        ACT phase: Execute planned actions

        Returns:
            Action results and observations
        """
        agents_needed = plan.get("agents_needed", ["research"])
        subtasks = plan.get("subtasks", [])

        action_results = {
            "observations": [],
            "agent_outputs": {},
            "complete": False,
            "answer": "",
        }

        # Execute subtasks with appropriate agents
        for task in subtasks:
            if "research" in task.lower() and "research" in self.agents:
                try:
                    result = await self.research_agent.conduct_research(task)
                    action_results["agent_outputs"]["research"] = result
                    action_results["observations"].append(
                        f"Research findings: {len(result.get('sources', []))} sources found"
                    )
                except Exception as e:
                    logger.error(f"Research agent error: {e}")

            elif "reason" in task.lower() and "reasoning" in self.agents:
                try:
                    result = await self.reasoning_agent.chain_of_thought(task)
                    action_results["agent_outputs"]["reasoning"] = result
                    action_results["observations"].append(
                        f"Reasoning result: {result.get('reasoning', '')[:100]}"
                    )
                except Exception as e:
                    logger.error(f"Reasoning agent error: {e}")

        # Mark as complete if we have substantial results
        action_results["complete"] = len(action_results["agent_outputs"]) > 0

        if action_results["agent_outputs"]:
            action_results["answer"] = self._synthesize_results(action_results["agent_outputs"])

        return action_results

    def _synthesize_results(self, outputs: Dict[str, Any]) -> str:
        """Synthesize results from agents into final answer"""
        synthesis = []

        if "research" in outputs:
            research = outputs["research"]
            synthesis.append(f"Research findings: {len(research.get('sources', []))} sources")
            for finding in research.get("findings", [])[:3]:
                synthesis.append(f"- {finding}")

        if "reasoning" in outputs:
            reasoning = outputs["reasoning"]
            if "reasoning" in reasoning:
                synthesis.append(f"Key insight: {reasoning.get('reasoning', '')[:200]}")

        return "\n".join(synthesis) if synthesis else "Task completed with results"

    async def route_task(self, task: str, agent_name: str) -> Optional[Any]:
        """
        Route task to specific agent

        Args:
            task: Task description
            agent_name: Name of agent to route to

        Returns:
            Agent result
        """
        agent = self.agents.get(agent_name.lower())
        if not agent:
            logger.warning(f"Unknown agent: {agent_name}")
            return None

        try:
            if agent_name.lower() == "research":
                return await agent.conduct_research(task)
            elif agent_name.lower() == "reasoning":
                return await agent.chain_of_thought(task)
        except Exception as e:
            logger.error(f"Error routing to {agent_name}: {e}")

        return None

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history

    def add_to_conversation(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of orchestrator execution"""
        return {
            "name": self.name,
            "tasks_completed": len(self.completed_tasks),
            "conversation_turns": len(self.conversation_history),
            "memory_stats": self.memory.get_memory_stats(),
            "working_memory": self.working_memory.get_summary(),
            "agents_available": list(self.agents.keys()),
            "tools_available": self.tool_registry.list_tools(),
        }

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool from the registry"""
        logger.info(f"Executing tool: {tool_name} with args: {kwargs}")
        return await self.tool_registry.execute_tool(tool_name, **kwargs)
