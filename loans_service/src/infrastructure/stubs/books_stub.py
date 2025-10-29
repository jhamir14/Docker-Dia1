from ...domain.ports.books_repo import BooksPort
from ..repositories.memory_store import BOOK_STATUS


class BooksStub(BooksPort):
    async def get_book(self, book_id: str):
        status = BOOK_STATUS.get(book_id, 'available')
        return {"id": book_id, "status": status}

    async def mark_loaned(self, book_id: str) -> None:
        BOOK_STATUS[book_id] = 'loaned'

    async def mark_returned(self, book_id: str) -> None:
        BOOK_STATUS[book_id] = 'available'