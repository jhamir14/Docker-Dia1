import httpx
import asyncio
import time
from ...domain.ports.users_repo import UsersPort
from ..logging.json_logger import logger


class UsersHTTP(UsersPort):
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

    async def get_user(self, user_id: str):
        logger.info("Getting user", extra={"user_id": user_id})
        result = await self._get(f"/api/users/{user_id}")
        logger.info("User retrieved successfully", extra={"user_id": user_id, "status": result.get("status")})
        return result

    async def get_user_active_loans_count(self, user_id: str) -> int:
        logger.info("Getting user active loans count", extra={"user_id": user_id})
        data = await self._get(f"/api/users/{user_id}/loans/count?status=active")
        count = data["count"]
        logger.info("User active loans count retrieved", extra={"user_id": user_id, "active_loans_count": count})
        return count