from ...domain.ports.users_repo import UsersPort
from ..repositories.memory_store import LOANS


class UsersStub(UsersPort):
    async def get_user(self, user_id: str):
        # Simula que el usuario existe y está activo
        return {"id": user_id, "status": "active"}

    async def get_user_active_loans_count(self, user_id: str) -> int:
        return sum(1 for l in LOANS.values() if l['user_id'] == user_id and l['status'] == 'active')