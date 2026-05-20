"""
Scraping engine orchestrator.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Optional

from .github import GitHubScraper
from .gitlab import GitLabScraper
from .models import RepositoryMetadata

logger = logging.getLogger("CodeScribe.Scraper.Engine")


class AsyncScraperEngine:
    """Orchestrates asynchronous repository discovery and ingestion."""

    def __init__(self, tokens: Optional[List[str]] = None, max_concurrency: int = 5):
        self.tokens = tokens or []
        self.github = GitHubScraper(tokens=self.tokens, max_concurrency=max_concurrency)
        self.gitlab = GitLabScraper(tokens=self.tokens, max_concurrency=max_concurrency)

    async def ingest_repositories(
        self,
        platform: str,
        query: str,
        output_dir: Path,
        limit: int = 100,
        download_source: bool = True,
    ):
        """Main ingestion pipeline."""
        scraper = self.github if platform == "github" else self.gitlab
        
        output_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = output_dir / "metadata.jsonl"
        
        logger.info(f"Starting ingestion of {limit} repositories from {platform}...")
        
        # We will use a queue to decouple searching from downloading
        repo_queue: asyncio.Queue = asyncio.Queue()
        
        # Start download workers
        workers = []
        if download_source:
            for i in range(5): # 5 concurrent download workers
                worker = asyncio.create_task(self._download_worker(f"worker-{i}", scraper, repo_queue, output_dir))
                workers.append(worker)

        count = 0
        async for repo in scraper.search_repositories(query=query, limit=limit):
            count += 1
            logger.info(f"[{count}/{limit}] Discovered: {repo.full_name} ({repo.stars} stars)")
            
            # Save metadata
            with open(metadata_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(repo.to_dict()) + "\n")
                
            if download_source:
                await repo_queue.put(repo)
                
        # Wait for queue to process
        if download_source:
            await repo_queue.join()
            
            # Cancel workers
            for w in workers:
                w.cancel()
            
        logger.info(f"Ingestion complete. Processed {count} repositories.")

    async def _download_worker(self, name: str, scraper, queue: asyncio.Queue, output_dir: Path):
        """Worker task to process downloading from the queue."""
        while True:
            repo: RepositoryMetadata = await queue.get()
            try:
                await scraper.download_zipball(repo, output_dir)
            except Exception as e:
                logger.error(f"{name} failed to download {repo.full_name}: {e}")
            finally:
                queue.task_done()
