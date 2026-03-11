"""Working Memory - Context window management and priority-based pruning"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """Item in working memory"""

    content: str
    priority: float = 0.5  # 0.0 to 1.0
    token_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "priority": self.priority,
            "token_count": self.token_count,
            "created_at": self.created_at.isoformat(),
            "relevance_score": self.relevance_score,
        }


class WorkingMemory:
    """
    Manages context window with sliding window and priority-based pruning.
    Keeps task-relevant information in the active context.
    """

    def __init__(
        self,
        max_tokens: int = 4000,
        reserve_tokens: int = 500,
        window_size: int = 5,
    ):
        """
        Initialize working memory

        Args:
            max_tokens: Maximum tokens to keep in context
            reserve_tokens: Tokens reserved for output
            window_size: Number of most recent items to always keep
        """
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens
        self.window_size = window_size
        self.items: List[MemoryItem] = []
        self.total_tokens = 0

    def add_item(
        self,
        content: str,
        priority: float = 0.5,
        token_count: Optional[int] = None,
    ) -> bool:
        """
        Add item to working memory

        Args:
            content: The content to store
            priority: Priority score (0.0 to 1.0)
            token_count: Estimated token count (auto-estimated if not provided)

        Returns:
            True if item was added, False if memory is full
        """
        if token_count is None:
            # Simple estimation: ~4 chars per token
            token_count = max(1, len(content) // 4)

        item = MemoryItem(
            content=content,
            priority=max(0.0, min(1.0, priority)),
            token_count=token_count,
        )

        # Check if adding this item would exceed capacity
        if self.total_tokens + token_count > self.available_tokens:
            self._prune_to_fit(token_count)

        self.items.append(item)
        self.total_tokens += token_count
        logger.debug(f"Added item to working memory. Total tokens: {self.total_tokens}")

        return True

    def _prune_to_fit(self, required_tokens: int) -> None:
        """Remove lowest-priority items to make room"""
        needed = self.total_tokens + required_tokens - self.available_tokens

        if needed <= 0:
            return

        # Always keep most recent window_size items
        protected_indices = set(range(max(0, len(self.items) - self.window_size), len(self.items)))

        # Sort by priority, keeping protected items
        pruneable = [
            (i, item)
            for i, item in enumerate(self.items)
            if i not in protected_indices
        ]
        pruneable.sort(key=lambda x: x[1].priority)

        tokens_freed = 0
        indices_to_remove = []

        for idx, item in pruneable:
            if tokens_freed >= needed:
                break
            indices_to_remove.append(idx)
            tokens_freed += item.token_count

        # Remove in reverse order to maintain indices
        for idx in sorted(indices_to_remove, reverse=True):
            removed = self.items.pop(idx)
            self.total_tokens -= removed.token_count
            logger.debug(f"Pruned low-priority item, freed {removed.token_count} tokens")

    def get_context(self, task_relevant_query: Optional[str] = None) -> str:
        """
        Get formatted context for LLM

        Args:
            task_relevant_query: Optional query to boost relevance of matching items

        Returns:
            Formatted context string
        """
        if not self.items:
            return ""

        # Calculate relevance scores if query provided
        if task_relevant_query:
            self._update_relevance_scores(task_relevant_query)

        # Sort by recency (most recent first) but also consider priority
        sorted_items = sorted(
            self.items,
            key=lambda x: (
                x.relevance_score * 0.4 + x.priority * 0.3 + x.created_at.timestamp() * 0.3
            ),
            reverse=True,
        )

        context_lines = []
        total = 0

        for item in sorted_items:
            if total + item.token_count <= self.available_tokens:
                context_lines.append(f"[Memory] {item.content}")
                total += item.token_count

        return "\n".join(context_lines)

    def _update_relevance_scores(self, query: str) -> None:
        """Update relevance scores based on query matching"""
        query_lower = query.lower()
        for item in self.items:
            # Simple keyword matching
            if query_lower in item.content.lower():
                item.relevance_score = 0.9
            else:
                # Check for semantic similarity with keywords
                query_words = set(query_lower.split())
                content_words = set(item.content.lower().split())
                overlap = len(query_words & content_words)
                item.relevance_score = min(1.0, overlap / max(len(query_words), 1) * 0.5)

    def clear(self) -> None:
        """Clear all working memory"""
        self.items = []
        self.total_tokens = 0
        logger.info("Cleared working memory")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            "items_count": len(self.items),
            "total_tokens": self.total_tokens,
            "available_tokens": self.available_tokens,
            "utilization": f"{self.total_tokens / self.available_tokens * 100:.1f}%",
            "avg_priority": sum(item.priority for item in self.items) / len(self.items)
            if self.items
            else 0,
        }

    def get_items(self) -> List[Dict[str, Any]]:
        """Get all items as dictionaries"""
        return [item.to_dict() for item in self.items]

    def update_item_priority(self, index: int, priority: float) -> bool:
        """Update priority of an item"""
        if 0 <= index < len(self.items):
            self.items[index].priority = max(0.0, min(1.0, priority))
            return True
        return False

    def compress_to_summary(self, max_summary_tokens: int = 500) -> str:
        """
        Create a summary of working memory for handoff to long-term memory
        In production, this would use LLM summarization
        """
        if not self.items:
            return ""

        # For now, just concatenate high-priority items
        summary_items = sorted(
            self.items,
            key=lambda x: x.priority,
            reverse=True,
        )

        summary_lines = []
        total_tokens = 0

        for item in summary_items:
            if total_tokens + item.token_count <= max_summary_tokens:
                summary_lines.append(item.content)
                total_tokens += item.token_count

        return "\n".join(summary_lines)
