"""
Agentic Research Assistant - Interactive CLI Interface

Usage:
    python main.py

Set OPENAI_API_KEY environment variable before running.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

from langchain_openai import ChatOpenAI

from src.agents.orchestrator import OrchestratorAgent
from src.memory.long_term_memory import LongTermMemory
from src.memory.working_memory import WorkingMemory
from src.tools.tool_registry import ToolRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("research_assistant.log"),
    ],
)
logger = logging.getLogger(__name__)


class ResearchAssistantCLI:
    """Interactive CLI for the research assistant"""

    def __init__(self):
        logger.info("Initializing Research Assistant...")

        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key,
        )

        # Initialize memory systems
        self.long_term_memory = LongTermMemory(persist_dir=".memory")
        self.working_memory = WorkingMemory(max_tokens=4000)

        # Initialize tool registry
        self.tool_registry = ToolRegistry()

        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent(
            llm=self.llm,
            memory=self.long_term_memory,
            working_memory=self.working_memory,
            tool_registry=self.tool_registry,
        )

        logger.info("Research Assistant initialized successfully")

    async def run(self):
        """Run the interactive CLI"""
        print("\n" + "=" * 60)
        print("Agentic Research Assistant - Multi-Agent Pipeline")
        print("=" * 60)
        print("\nCommands:")
        print("  'help'           - Show this help message")
        print("  'stats'          - Show memory and system stats")
        print("  'search <query>' - Conduct research on a topic")
        print("  'reason <task>'  - Use reasoning on a task")
        print("  'quit'           - Exit the assistant")
        print("\nOr just ask a question and the assistant will decompose it.\n")

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("Goodbye!")
                    break

                if user_input.lower() == "help":
                    self._show_help()
                    continue

                if user_input.lower() == "stats":
                    self._show_stats()
                    continue

                if user_input.lower().startswith("search "):
                    query = user_input[7:].strip()
                    await self._handle_search(query)
                    continue

                if user_input.lower().startswith("reason "):
                    task = user_input[7:].strip()
                    await self._handle_reasoning(task)
                    continue

                # Default: use orchestrator to decompose and execute
                await self._handle_general_query(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                print(f"Error: {e}")

    async def _handle_search(self, query: str):
        """Handle research/search request"""
        print(f"\nAssistant: Researching '{query}'...")

        try:
            result = await self.orchestrator.research_agent.conduct_research(query)
            print(f"\nFound {len(result['sources'])} sources:")
            for source in result["sources"][:3]:
                print(f"\n- {source['title']}")
                print(f"  Authors: {source['authors']}")
                print(f"  {source['summary'][:200]}...")

            if result["findings"]:
                print("\nKey Findings:")
                for finding in result["findings"][:5]:
                    print(f"- {finding}")

        except Exception as e:
            logger.error(f"Search error: {e}")
            print(f"Error conducting research: {e}")

    async def _handle_reasoning(self, task: str):
        """Handle reasoning request"""
        print(f"\nAssistant: Analyzing '{task}'...")

        try:
            result = await self.orchestrator.reasoning_agent.chain_of_thought(task)
            print(f"\nReasoning Steps:")
            for step in result.get("steps", [])[:5]:
                print(f"  {step}")
            print(f"\nConclusion:\n{result['reasoning'][:400]}...")

        except Exception as e:
            logger.error(f"Reasoning error: {e}")
            print(f"Error during reasoning: {e}")

    async def _handle_general_query(self, query: str):
        """Handle general query with full Plan→Reason→Act loop"""
        print(f"\nAssistant: Processing your query...")

        try:
            result = await self.orchestrator.execute_task(query, max_iterations=3)

            print(f"\nExecution Summary:")
            print(f"- Iterations: {len(result['iterations'])}")
            print(f"- Sources used: {len(result['sources_used'])}")

            print(f"\nAnswer:")
            print(result["final_answer"])

            # Show memory usage
            stats = self.long_term_memory.get_memory_stats()
            print(f"\nMemory used:")
            print(f"- Total memories: {stats['total_memories']}")
            print(f"- Average importance: {stats['avg_importance']:.2f}")

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            print(f"Error: {e}")

    def _show_help(self):
        """Show help message"""
        print("\nAvailable Commands:")
        print("  search <query>   - Search for information on a topic")
        print("  reason <task>    - Perform reasoning on a problem")
        print("  stats            - Show system statistics")
        print("  help             - Show this help")
        print("  quit             - Exit\n")

    def _show_stats(self):
        """Show system statistics"""
        print("\n" + "=" * 40)
        print("System Statistics")
        print("=" * 40)

        # Orchestrator stats
        exec_summary = self.orchestrator.get_execution_summary()
        print(f"\nOrchestrator:")
        print(f"  Tasks completed: {exec_summary['tasks_completed']}")
        print(f"  Conversation turns: {exec_summary['conversation_turns']}")
        print(f"  Agents: {', '.join(exec_summary['agents_available'])}")

        # Memory stats
        mem_stats = exec_summary["memory_stats"]
        print(f"\nLong-term Memory:")
        print(f"  Total entries: {mem_stats['total_memories']}")
        print(f"  Total uses: {mem_stats['total_uses']}")
        print(f"  Avg importance: {mem_stats['avg_importance']:.2f}")
        if mem_stats["by_type"]:
            print(f"  By type: {mem_stats['by_type']}")

        # Working memory stats
        wm_stats = exec_summary["working_memory"]
        print(f"\nWorking Memory:")
        print(f"  Items: {wm_stats['items_count']}")
        print(f"  Utilization: {wm_stats['utilization']}")

        # Tools
        print(f"\nAvailable Tools:")
        for tool in exec_summary["tools_available"]:
            print(f"  - {tool}")

        print()

    def save_checkpoint(self):
        """Save memory checkpoint"""
        checkpoint_path = ".checkpoint.json"
        self.long_term_memory.save_checkpoint(checkpoint_path)
        logger.info(f"Checkpoint saved to {checkpoint_path}")


async def main():
    """Main entry point"""
    try:
        cli = ResearchAssistantCLI()
        await cli.run()
        cli.save_checkpoint()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
