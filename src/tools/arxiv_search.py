"""ArXiv research paper search and retrieval"""

import logging
from typing import List, Dict, Optional
import arxiv

logger = logging.getLogger(__name__)


class ArxivSearch:
    """Interface for searching and retrieving academic papers from ArXiv"""

    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.client = arxiv.Client()

    def search(
        self, query: str, max_results: Optional[int] = None, sort_by: str = "relevance"
    ) -> List[Dict[str, str]]:
        """
        Search for papers on ArXiv

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criteria (relevance, lastUpdatedDate, submittedDate)

        Returns:
            List of paper dictionaries with title, authors, summary, etc.
        """
        results_limit = max_results or self.max_results
        try:
            # Map sort options to arxiv.SortCriterion
            sort_map = {
                "relevance": arxiv.SortCriterion.Relevance,
                "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
                "submittedDate": arxiv.SortCriterion.SubmittedDate,
            }
            sort_criterion = sort_map.get(sort_by, arxiv.SortCriterion.Relevance)

            papers = []
            search = arxiv.Search(
                query=query,
                max_results=results_limit,
                sort_by=sort_criterion,
                sort_order=arxiv.SortOrder.Descending,
            )

            for paper in self.client.results(search):
                papers.append(
                    {
                        "title": paper.title,
                        "authors": ", ".join([author.name for author in paper.authors]),
                        "published": paper.published.isoformat(),
                        "summary": paper.summary,
                        "arxiv_id": paper.arxiv_id,
                        "url": paper.arxiv_url,
                        "pdf_url": paper.pdf_url,
                    }
                )

            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers
        except Exception as e:
            logger.error(f"Error searching ArXiv: {str(e)}")
            return []

    def search_by_author(self, author: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """Search papers by author"""
        query = f'au:"{author}"'
        return self.search(query, max_results)

    def search_by_category(self, category: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """Search papers by category (e.g., 'cs.AI', 'stat.ML')"""
        query = f"cat:{category}"
        return self.search(query, max_results)

    def search_recent(self, query: str, days: int = 7, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """Search for recent papers (submitted in last N days)"""
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        query_with_date = f"{query} AND submittedDate:[{cutoff_date} TO 2099-12-31]"
        return self.search(query_with_date, max_results, sort_by="submittedDate")

    def get_paper_details(self, arxiv_id: str) -> Optional[Dict[str, str]]:
        """Get detailed information about a specific paper"""
        try:
            paper = next(
                self.client.results(arxiv.Search(id_list=[arxiv_id]))
            )
            return {
                "title": paper.title,
                "authors": ", ".join([author.name for author in paper.authors]),
                "published": paper.published.isoformat(),
                "summary": paper.summary,
                "arxiv_id": paper.arxiv_id,
                "url": paper.arxiv_url,
                "pdf_url": paper.pdf_url,
                "categories": paper.categories,
            }
        except Exception as e:
            logger.error(f"Error fetching paper {arxiv_id}: {str(e)}")
            return None

    def extract_citations(self, paper_summary: str) -> List[str]:
        """Extract potential citations from paper summary"""
        # Simple heuristic: look for patterns like "Smith et al." or "[1]"
        import re

        citations = []
        # Pattern for author citations
        author_pattern = r"[A-Z][a-z]+ et al\."
        citations.extend(re.findall(author_pattern, paper_summary))

        # Pattern for reference numbers
        ref_pattern = r"\[\d+\]"
        citations.extend(re.findall(ref_pattern, paper_summary))

        return list(set(citations))  # Remove duplicates
