"""Reasoning Agent - Specialist for analysis and logical inference"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from src.memory.long_term_memory import LongTermMemory
from src.memory.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """
    Specialized agent for reasoning tasks.
    Focuses on analysis, chain-of-thought reasoning, and logical inference.
    """

    def __init__(
        self,
        llm: ChatOpenAI,
        memory: LongTermMemory,
        working_memory: WorkingMemory,
    ):
        self.llm = llm
        self.memory = memory
        self.working_memory = working_memory
        self.conversation_history = []
        self.name = "ReasoningAgent"

    async def chain_of_thought(self, problem: str, context: str = "") -> Dict[str, Any]:
        """
        Perform chain-of-thought reasoning

        Args:
            problem: Problem to reason through
            context: Additional context

        Returns:
            Reasoning steps and conclusion
        """
        logger.info(f"Starting chain-of-thought for: {problem}")

        system_prompt = """You are an expert reasoner. Use chain-of-thought to solve problems.
        Structure your response as:
        1. Problem Understanding
        2. Key Assumptions
        3. Reasoning Steps (numbered)
        4. Intermediate Conclusions
        5. Final Conclusion

        Be thorough and explicit about your reasoning."""

        full_context = f"{context}\n\nProblem: {problem}" if context else problem

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=full_context),
        ]

        response = self.llm.invoke(messages)

        reasoning_result = {
            "problem": problem,
            "reasoning": response.content,
            "timestamp": datetime.now().isoformat(),
        }

        # Parse reasoning steps from response
        steps = self._parse_reasoning_steps(response.content)
        reasoning_result["steps"] = steps

        # Store in memory
        self.memory.add_memory(
            f"Reasoning: {problem}. Conclusion: {response.content[-200:]}",
            memory_type="reasoning",
            tags=["cot", "analysis"],
            importance=0.8,
        )

        # Add to working memory
        self.working_memory.add_item(
            f"Reasoning conclusion: {response.content[-200:]}",
            priority=0.8,
            token_count=100,
        )

        return reasoning_result

    def _parse_reasoning_steps(self, response: str) -> List[str]:
        """Parse numbered reasoning steps from response"""
        steps = []
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                steps.append(line)
        return steps

    async def generate_hypotheses(
        self, scenario: str, num_hypotheses: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate and evaluate multiple hypotheses

        Args:
            scenario: Scenario to hypothesize about
            num_hypotheses: Number of hypotheses to generate

        Returns:
            List of hypotheses with evaluations
        """
        logger.info(f"Generating {num_hypotheses} hypotheses for: {scenario}")

        system_prompt = f"""Generate {num_hypotheses} distinct hypotheses for the given scenario.
        For each, provide:
        1. Hypothesis statement
        2. Supporting evidence
        3. Potential objections
        4. Testability score (0-1)
        5. Plausibility score (0-1)

        Return as JSON array."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Scenario: {scenario}"),
        ]

        response = self.llm.invoke(messages)

        hypotheses = []
        try:
            hypotheses = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback: extract text-based hypotheses
            hypotheses = [
                {"statement": scenario, "plausibility": 0.5}
            ]

        # Store each hypothesis
        for i, hyp in enumerate(hypotheses):
            self.memory.add_memory(
                f"Hypothesis {i+1}: {str(hyp).split(':')[0][:100]}",
                memory_type="reasoning",
                tags=["hypothesis", scenario.split()[0]],
                importance=0.7,
            )

        return hypotheses

    async def comparative_analysis(
        self, items: List[str], criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Perform comparative analysis of multiple items

        Args:
            items: Items to compare
            criteria: Criteria for comparison

        Returns:
            Comparison matrix and summary
        """
        logger.info(f"Comparing {len(items)} items on {len(criteria)} criteria")

        system_prompt = """Perform a detailed comparative analysis.
        Create a comparison matrix and provide summary insights.
        Return as JSON with 'matrix' (dict of dicts) and 'summary' (string)."""

        prompt = f"""Compare these items: {', '.join(items)}
        Using these criteria: {', '.join(criteria)}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ]

        response = self.llm.invoke(messages)

        result = {
            "items": items,
            "criteria": criteria,
            "analysis": response.content,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            parsed = json.loads(response.content)
            result.update(parsed)
        except json.JSONDecodeError:
            pass

        # Store analysis
        self.memory.add_memory(
            f"Comparative analysis of {items}: {response.content[:200]}",
            memory_type="reasoning",
            tags=["comparison", "analysis"],
        )

        return result

    async def fact_check(self, claims: List[str], sources: List[str] = None) -> Dict[str, Any]:
        """
        Check facts and claims

        Args:
            claims: Claims to verify
            sources: Optional authoritative sources

        Returns:
            Fact-check results
        """
        logger.info(f"Fact-checking {len(claims)} claims")

        source_context = ""
        if sources:
            source_context = f"\nAuthoritative sources: {', '.join(sources)}"

        system_prompt = f"""You are a fact-checker. Evaluate each claim:
        1. Assess accuracy (true/false/unclear)
        2. Provide evidence
        3. Identify potential biases
        4. Rate confidence (0-1)

        Return as JSON array with results."""

        claims_text = "\n".join([f"- {claim}" for claim in claims])
        prompt = f"Claims to check:{claims_text}{source_context}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt),
        ]

        response = self.llm.invoke(messages)

        result = {
            "claims": claims,
            "verifications": [],
            "summary": response.content,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            verifications = json.loads(response.content)
            result["verifications"] = verifications if isinstance(verifications, list) else []
        except json.JSONDecodeError:
            pass

        # Store fact-check
        self.memory.add_memory(
            f"Fact-check: {len(claims)} claims. Result: {response.content[:150]}",
            memory_type="reasoning",
            tags=["fact-check", "verification"],
        )

        return result

    async def synthesize_insights(
        self, information: List[str], theme: str = ""
    ) -> Dict[str, Any]:
        """
        Synthesize information into coherent insights

        Args:
            information: List of information pieces
            theme: Optional theme for synthesis

        Returns:
            Synthesized insights
        """
        logger.info(f"Synthesizing {len(information)} pieces of information")

        system_prompt = """You are an insight synthesizer.
        Combine the provided information into coherent, actionable insights.
        Identify patterns, connections, and implications.
        Return as JSON with 'insights' (array) and 'implications' (array)."""

        info_text = "\n".join([f"- {info}" for info in information])
        theme_clause = f"\nTheme: {theme}" if theme else ""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Information:{info_text}{theme_clause}"),
        ]

        response = self.llm.invoke(messages)

        result = {
            "information_count": len(information),
            "theme": theme,
            "synthesis": response.content,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            parsed = json.loads(response.content)
            result.update(parsed)
        except json.JSONDecodeError:
            pass

        # Store synthesis
        self.memory.add_memory(
            f"Synthesis of {len(information)} items on '{theme}': {response.content[:200]}",
            memory_type="reasoning",
            tags=["synthesis", "insights"],
        )

        return result

    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """Get history of reasoning in this session"""
        reasoning_memories = self.memory.search_by_type("reasoning", limit=10)
        return reasoning_memories
