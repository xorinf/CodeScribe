"""
GitHub scraper integration for CodeScribe.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Dict, Any
import aiohttp
import aiofiles

from .models import RepositoryMetadata

logger = logging.getLogger("CodeScribe.Scraper.GitHub")


class GitHubScraper:
    """Handles asynchronous scraping of GitHub repositories."""

    BASE_URL = "https://api.github.com"

    def __init__(self, tokens: Optional[List[str]] = None, max_concurrency: int = 5):
        self.tokens = tokens or []
        self.token_idx = 0
        self.semaphore = asyncio.Semaphore(max_concurrency)

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeScribe-Scraper",
        }
        if self.tokens:
            headers["Authorization"] = f"token {self.tokens[self.token_idx]}"
        return headers

    def _rotate_token(self):
        """Rotate to the next available token if multiple are provided."""
        if self.tokens:
            self.token_idx = (self.token_idx + 1) % len(self.tokens)
            logger.debug(f"Rotated GitHub token to index {self.token_idx}")

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse):
        """Check rate limits and wait if necessary."""
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        if remaining <= 0:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            import time
            wait_time = max(reset_time - int(time.time()), 0) + 1
            logger.warning(f"GitHub API rate limit exceeded. Waiting {wait_time}s or rotating token.")
            if len(self.tokens) > 1:
                self._rotate_token()
            else:
                await asyncio.sleep(wait_time)

    async def search_repositories(
        self, query: str, sort: str = "stars", order: str = "desc", limit: int = 100
    ) -> AsyncGenerator[RepositoryMetadata, None]:
        """Search for repositories on GitHub and yield metadata."""
        url = f"{self.BASE_URL}/search/repositories"
        page = 1
        fetched = 0

        async with aiohttp.ClientSession() as session:
            while fetched < limit:
                params = {
                    "q": query,
                    "sort": sort,
                    "order": order,
                    "per_page": min(100, limit - fetched),
                    "page": page,
                }
                
                async with self.semaphore:
                    async with session.get(url, headers=self._get_headers(), params=params) as response:
                        if response.status in (403, 429):
                            await self._handle_rate_limit(response)
                            continue # Retry current page
                            
                        if response.status != 200:
                            logger.error(f"GitHub search failed: {response.status} - {await response.text()}")
                            break
                        
                        data = await response.json()
                        items = data.get("items", [])
                        
                        if not items:
                            break # No more results
                            
                        for item in items:
                            if fetched >= limit:
                                break
                            
                            metadata = RepositoryMetadata(
                                platform="github",
                                id=str(item["id"]),
                                owner=item["owner"]["login"],
                                name=item["name"],
                                full_name=item["full_name"],
                                url=item["html_url"],
                                description=item.get("description"),
                                language=item.get("language"),
                                stars=item.get("stargazers_count", 0),
                                forks=item.get("forks_count", 0),
                                default_branch=item.get("default_branch", "main"),
                                topics=item.get("topics", []),
                                license=item.get("license", {}).get("key") if item.get("license") else None,
                                updated_at=item.get("updated_at"),
                            )
                            fetched += 1
                            yield metadata
                            
                page += 1
                await asyncio.sleep(1) # Be nice to the API

    async def download_zipball(self, repo: RepositoryMetadata, output_dir: Path) -> Optional[Path]:
        """Download the repository zipball."""
        url = f"{self.BASE_URL}/repos/{repo.full_name}/zipball/{repo.default_branch}"
        dest_path = output_dir / f"{repo.owner}_{repo.name}.zip"
        
        # Don't re-download if it exists
        if dest_path.exists():
            logger.debug(f"Zipball already exists: {dest_path}")
            return dest_path

        async with aiohttp.ClientSession() as session:
            async with self.semaphore:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status in (403, 429):
                        await self._handle_rate_limit(response)
                        return await self.download_zipball(repo, output_dir) # Retry
                        
                    if response.status == 302: # GitHub returns redirect for zipball
                         redirect_url = response.headers.get("Location")
                         if redirect_url:
                             async with session.get(redirect_url) as redirect_resp:
                                  return await self._save_file(redirect_resp, dest_path)
                    
                    if response.status != 200:
                        logger.error(f"Failed to download zipball for {repo.full_name}: {response.status}")
                        return None
                        
                    return await self._save_file(response, dest_path)

    async def _save_file(self, response: aiohttp.ClientResponse, dest_path: Path) -> Path:
        """Helper to stream response body to file asynchronously."""
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(dest_path, 'wb') as f:
            async for chunk in response.content.iter_chunked(8192):
                await f.write(chunk)
        logger.info(f"Downloaded zipball to {dest_path}")
        return dest_path
