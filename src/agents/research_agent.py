"""Research Agent - Specialist for web search and academic research"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from src.memory.long_term_memory import LongTermMemory
from src.memory.working_memory import WorkingMemory
from src.tools.arxiv_search import ArxivSearch

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Specialized agent for conducting research tasks.
    Focuses on web search, academic paper retrieval, and information gathering.
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
        self.arxiv = ArxivSearch(max_results=10)
        self.conversation_history = []
        self.name = "ResearchAgent"

    def plan_research(self, query: str) -> Dict[str, Any]:
        """
        Plan the research approach

        Args:
            query: Research query

        Returns:
            Plan dict with search terms, strategies, and goals
        """
        system_prompt = """You are a research planning specialist.
        Given a research query, create a detailed plan including:
        1. Expanded search terms and queries
        2. Research strategies (academic papers, recent news, etc.)
        3. Expected information types
        4. Evaluation criteria for sources

        Return a JSON object with your plan."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Plan research for: {query}"),
        ]

        response = self.llm.invoke(messages)

        try:
            plan = json.loads(response.content)
        except json.JSONDecodeError:
            plan = {"query": query, "strategies": ["general search", "academic papers"]}

        # Store plan in memory
        self.memory.add_memory(
            f"Research Plan for '{query}': {json.dumps(plan)}",
            memory_type="research",
            tags=["planning", query.split()[0]],
        )

        return plan

    async def conduct_research(self, query: str, depth: str = "standard") -> Dict[str, Any]:
        """
        Conduct research on a topic

        Args:
            query: Research query
            depth: research depth ('quick', 'standard', 'deep')

        Returns:
            Research results
        """
        logger.info(f"Conducting {depth} research for: {query}")

        # Plan the research
        plan = self.plan_research(query)

        # Add to working memory
        self.working_memory.add_item(
            f"Research Query: {query}",
            priority=0.9,
            token_count=50,
        )

        results = {
            "query": query,
            "depth": depth,
            "plan": plan,
            "sources": [],
            "findings": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Search academic papers
        if depth in ["standard", "deep"]:
            papers = self.arxiv.search(
                query,
                max_results=5 if depth == "standard" else 10
            )
            results["sources"].extend(papers)

            # Store papers in memory
            for paper in papers:
                self.memory.add_memory(
                    f"Paper: {paper['title']} by {paper['authors']}. Summary: {paper['summary'][:200]}",
                    memory_type="research",
                    tags=["paper", query.split()[0]],
                    importance=0.7,
                )

        # Synthesize findings
        if results["sources"]:
            findings = await self._synthesize_findings(query, results["sources"])
            results["findings"] = findings

        # Store research session in memory
        self.memory.add_memory(
            f"Research Session: {query} - Found {len(results['sources'])} sources",
            memory_type="research",
            tags=["session", query.split()[0]],
        )

        return results

    async def _synthesize_findings(
        self, query: str, sources: List[Dict[str, str]]
    ) -> List[str]:
        """Synthesize findings from sources"""
        if not sources:
            return []

        source_summaries = "\n".join(
            [f"- {s['title']}: {s['summary'][:100]}..." for s in sources[:3]]
        )

        system_prompt = """You are a research synthesizer.
        Analyze the provided sources and extract key findings.
        List the most important findings as bullet points."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"Query: {query}\n\nSources:\n{source_summaries}"
            ),
        ]

        response = self.llm.invoke(messages)

        # Parse response into findings
        findings = [
            line.strip()
            for line in response.content.split("\n")
            if line.strip() and line.strip().startswith("-")
        ]

        return findings

    def expand_query(self, query: str) -> List[str]:
        """Expand a query into related search terms"""
        system_prompt = """Generate 5 expanded search terms related to the query.
        Return as JSON list of strings only."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Query: {query}"),
        ]

        response = self.llm.invoke(messages)

        try:
            expanded = json.loads(response.content)
            return expanded if isinstance(expanded, list) else [query]
        except json.JSONDecodeError:
            return [query]

    def extract_citations(self, sources: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format sources as citations"""
        citations = []
        for source in sources:
            citation = {
                "title": source.get("title", "Unknown"),
                "authors": source.get("authors", "Unknown"),
                "url": source.get("url", source.get("pdf_url", "")),
                "date": source.get("published", ""),
                "arxiv_id": source.get("arxiv_id", ""),
            }
            citations.append(citation)

        return citations

    async def evaluate_source_quality(self, source: Dict[str, str]) -> float:
        """
        Evaluate quality of a research source

        Returns:
            Quality score 0.0 to 1.0
        """
        system_prompt = """Evaluate the quality of an academic source.
        Consider: recency, author reputation indicators, citation count potential.
        Return a single number between 0.0 and 1.0."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"Title: {source.get('title')}\n"
                f"Authors: {source.get('authors')}\n"
                f"Date: {source.get('published')}"
            ),
        ]

        response = self.llm.invoke(messages)

        try:
            return float(response.content)
        except (ValueError, AttributeError):
            return 0.5

    def get_research_summary(self) -> str:
        """Get summary of research conducted in this session"""
        stats = self.memory.get_memory_stats()
        research_memories = self.memory.search_by_type("research", limit=5)

        summary = f"Research Summary:\n"
        summary += f"- Total research memories: {len(research_memories)}\n"
        summary += f"- Session: {stats['session_id']}\n"
        summary += f"- Recent findings:\n"

        for mem in research_memories:
            summary += f"  * {mem['content'][:100]}...\n"

        return summary
