import httpx
import asyncio
import time
from ...domain.ports.books_repo import BooksPort
from ..logging.json_logger import logger


class BooksHTTP(BooksPort):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=3.0)

    async def _get(self, path: str):
        url = f"{self.base_url}{path}"
        for attempt in range(3):
            start_time = time.time()
            try:
                logger.info("HTTP request started", extra={
                    "http_method": "GET",
                    "url": url,
                    "attempt": attempt + 1
                })
                
                r = await self.client.get(url)
                duration_ms = int((time.time() - start_time) * 1000)
                
                r.raise_for_status()
                
                logger.info("HTTP request successful", extra={
                    "http_method": "GET",
                    "url": url,
                    "http_status": r.status_code,
                    "duration_ms": duration_ms,
                    "attempt": attempt + 1
                })
                
                return r.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.warning("HTTP request failed", extra={
                    "http_method": "GET",
                    "url": url,
                    "http_status": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                    "duration_ms": duration_ms,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                
                if attempt >= 2:
                    logger.error("HTTP request failed after all retries", extra={
                        "http_method": "GET",
                        "url": url,
                        "total_attempts": 3,
                        "error": str(e)
                    })
                    raise
                await asyncio.sleep(0.2)

    async def _post_no_content(self, path: str):
        for attempt in range(3):
            try:
                r = await self.client.post(f"{self.base_url}{path}")
                r.raise_for_status()
                if r.status_code != 204:
                    raise httpx.HTTPStatusError("Expected 204", request=r.request, response=r)
                return
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning("books_http error attempt=%s %s", attempt, str(e))
                if attempt >= 2:
                    raise
                await asyncio.sleep(0.2)

    async def get_book(self, book_id: str):
        logger.info("Getting book", extra={"book_id": book_id})
        result = await self._get(f"/api/books/{book_id}")
        logger.info("Book retrieved successfully", extra={"book_id": book_id, "status": result.get("status")})
        return result

    async def mark_loaned(self, book_id: str) -> None:
        await self._post_no_content(f"/api/books/{book_id}/loaned")

    async def mark_returned(self, book_id: str) -> None:
        await self._post_no_content(f"/api/books/{book_id}/returned")