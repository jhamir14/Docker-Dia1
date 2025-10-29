import os
from ...domain.services.loan_service import LoanDomainService
from ...infrastructure.repositories.loans_repo_django import LoansRepoMemory
from ...infrastructure.stubs.users_stub import UsersStub
from ...infrastructure.stubs.books_stub import BooksStub
from ...infrastructure.http_adapters.users_http import UsersHTTP
from ...infrastructure.http_adapters.books_http import BooksHTTP
from ...infrastructure.services.clock_system import SystemClock
from ...infrastructure.services.uuid_native import NativeUuid


# Configuración mínima: por defecto usa stubs en memoria.
# Si se define USERS_BASE_URL o BOOKS_BASE_URL se usarán los adaptadores HTTP reales.
USERS_BASE_URL = os.getenv("USERS_BASE_URL")
BOOKS_BASE_URL = os.getenv("BOOKS_BASE_URL")

_clock = SystemClock()
_uuid = NativeUuid()
_repo = LoansRepoMemory()

if USERS_BASE_URL:
    _users = UsersHTTP(USERS_BASE_URL)
else:
    _users = UsersStub()

if BOOKS_BASE_URL:
    _books = BooksHTTP(BOOKS_BASE_URL)
else:
    _books = BooksStub()

_service = LoanDomainService(
    users=_users,
    books=_books,
    loans=_repo,
    clock=_clock,
    uuidgen=_uuid,
)


def get_service() -> LoanDomainService:
    return _service