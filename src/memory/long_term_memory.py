"""Long-Term Memory System with ChromaDB Backend"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid

logger = logging.getLogger(__name__)


class MemoryEntry:
    """Represents a single memory entry"""

    def __init__(
        self,
        content: str,
        memory_type: str = "general",
        session_id: str = None,
        tags: List[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.memory_type = memory_type  # general, research, reasoning, query, result
        self.session_id = session_id or str(uuid.uuid4())
        self.tags = tags or []
        self.created_at = datetime.now()
        self.accessed_at = datetime.now()
        self.importance = 0.5  # 0.0 to 1.0
        self.use_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "session_id": self.session_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "importance": self.importance,
            "use_count": self.use_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary"""
        entry = cls(
            content=data["content"],
            memory_type=data.get("memory_type", "general"),
            session_id=data.get("session_id"),
            tags=data.get("tags", []),
        )
        entry.id = data["id"]
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.accessed_at = datetime.fromisoformat(data["accessed_at"])
        entry.importance = data.get("importance", 0.5)
        entry.use_count = data.get("use_count", 0)
        return entry


class LongTermMemory:
    """Persistent memory system using ChromaDB for semantic search"""

    def __init__(self, persist_dir: str = ".memory_cache"):
        self.persist_dir = persist_dir
        self.memories: Dict[str, MemoryEntry] = {}
        self.session_id = str(uuid.uuid4())

        try:
            import chromadb

            self.chroma_client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name="research_memories",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Initialized ChromaDB at {persist_dir}")
        except ImportError:
            logger.warning("ChromaDB not available, using in-memory storage only")
            self.chroma_client = None
            self.collection = None

    def add_memory(
        self,
        content: str,
        memory_type: str = "general",
        tags: List[str] = None,
        importance: float = 0.5,
    ) -> str:
        """Add a new memory entry"""
        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            session_id=self.session_id,
            tags=tags,
        )
        entry.importance = importance

        self.memories[entry.id] = entry

        # Store in ChromaDB if available
        if self.collection is not None:
            try:
                self.collection.add(
                    ids=[entry.id],
                    documents=[content],
                    metadatas=[
                        {
                            "memory_type": memory_type,
                            "session_id": self.session_id,
                            "tags": ",".join(tags or []),
                            "created_at": entry.created_at.isoformat(),
                            "importance": str(importance),
                        }
                    ],
                )
                logger.debug(f"Added memory entry {entry.id} to ChromaDB")
            except Exception as e:
                logger.error(f"Error adding to ChromaDB: {e}")

        logger.info(f"Added memory: {memory_type} (ID: {entry.id})")
        return entry.id

    def search_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memories semantically using ChromaDB"""
        if self.collection is None:
            logger.warning("ChromaDB not available, falling back to keyword search")
            return self._search_keyword(query, limit)

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
            )

            memories = []
            if results and results["ids"] and len(results["ids"]) > 0:
                for i, entry_id in enumerate(results["ids"][0]):
                    if entry_id in self.memories:
                        entry = self.memories[entry_id]
                        entry.accessed_at = datetime.now()
                        entry.use_count += 1
                        memories.append(
                            {
                                "id": entry.id,
                                "content": entry.content,
                                "type": entry.memory_type,
                                "distance": results["distances"][0][i] if results["distances"] else 0,
                                "created_at": entry.created_at.isoformat(),
                            }
                        )

            logger.info(f"Semantic search found {len(memories)} results for: {query}")
            return memories
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._search_keyword(query, limit)

    def _search_keyword(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fallback keyword search"""
        query_lower = query.lower()
        matches = []

        for entry in self.memories.values():
            if query_lower in entry.content.lower():
                matches.append(
                    {
                        "id": entry.id,
                        "content": entry.content,
                        "type": entry.memory_type,
                        "created_at": entry.created_at.isoformat(),
                    }
                )

        return sorted(
            matches, key=lambda x: self.memories[x["id"]].importance, reverse=True
        )[:limit]

    def search_by_type(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by type"""
        matches = [
            {
                "id": entry.id,
                "content": entry.content,
                "type": entry.memory_type,
                "created_at": entry.created_at.isoformat(),
            }
            for entry in self.memories.values()
            if entry.memory_type == memory_type
        ]

        return sorted(
            matches, key=lambda x: self.memories[x["id"]].accessed_at, reverse=True
        )[:limit]

    def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by tags"""
        matches = []
        for entry in self.memories.values():
            if any(tag in entry.tags for tag in tags):
                matches.append(
                    {
                        "id": entry.id,
                        "content": entry.content,
                        "type": entry.memory_type,
                        "tags": entry.tags,
                        "created_at": entry.created_at.isoformat(),
                    }
                )

        return sorted(
            matches, key=lambda x: self.memories[x["id"]].importance, reverse=True
        )[:limit]

    def consolidate_memories(self, days: int = 7) -> int:
        """
        Consolidate old memories to save space
        This is where you'd implement summarization of old memories
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        old_entries = [
            entry_id
            for entry_id, entry in self.memories.items()
            if entry.created_at < cutoff_date and entry.use_count < 2
        ]

        # In production, these would be summarized and compressed
        # For now, we just log them
        logger.info(f"Identified {len(old_entries)} old memories for consolidation")
        return len(old_entries)

    def update_importance(self, entry_id: str, importance: float) -> bool:
        """Update the importance score of a memory"""
        if entry_id not in self.memories:
            return False

        self.memories[entry_id].importance = max(0.0, min(1.0, importance))
        return True

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        return {
            "total_memories": len(self.memories),
            "session_id": self.session_id,
            "by_type": {
                mtype: sum(1 for e in self.memories.values() if e.memory_type == mtype)
                for mtype in set(e.memory_type for e in self.memories.values())
            },
            "total_uses": sum(e.use_count for e in self.memories.values()),
            "avg_importance": (
                sum(e.importance for e in self.memories.values())
                / len(self.memories)
                if self.memories
                else 0
            ),
        }

    def save_checkpoint(self, filepath: str) -> None:
        """Save memory checkpoint to file"""
        checkpoint = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "memories": {
                entry_id: entry.to_dict()
                for entry_id, entry in self.memories.items()
            },
        }
        with open(filepath, "w") as f:
            json.dump(checkpoint, f, indent=2)
        logger.info(f"Saved memory checkpoint to {filepath}")

    def load_checkpoint(self, filepath: str) -> None:
        """Load memory checkpoint from file"""
        try:
            with open(filepath, "r") as f:
                checkpoint = json.load(f)
            self.session_id = checkpoint["session_id"]
            self.memories = {
                entry_id: MemoryEntry.from_dict(entry)
                for entry_id, entry in checkpoint["memories"].items()
            }
            logger.info(f"Loaded memory checkpoint from {filepath}")
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
