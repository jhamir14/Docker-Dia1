from typing import Optional
from ...domain.ports.loans_repo import LoansPort
from .memory_store import LOANS


class LoansRepoMemory(LoansPort):
    async def save(self, loan: dict) -> None:
        LOANS[loan['loan_id']] = loan

    async def get(self, loan_id: str) -> Optional[dict]:
        return LOANS.get(loan_id)

    async def mark_returned(self, loan_id: str) -> None:
        if loan_id in LOANS:
            LOANS[loan_id]['status'] = 'returned'


class LoansDjangoRepo(LoansPort):
    """
    Ejemplo mínimo de repositorio usando Django ORM.
    Requiere pasar un LoanModel (Django) con campos: loan_id, user_id, book_id, start_date, due_date, status.
    """

    def __init__(self, LoanModel):
        self.LoanModel = LoanModel

    async def save(self, loan: dict):
        obj = self.LoanModel.objects.create(
            loan_id=loan['loan_id'],
            user_id=loan['user_id'],
            book_id=loan['book_id'],
            start_date=loan['start_date'],
            due_date=loan['due_date'],
            status=loan['status'],
        )
        return obj

    async def get(self, loan_id: str):
        try:
            o = self.LoanModel.objects.get(loan_id=loan_id)
            return {
                'loan_id': o.loan_id,
                'user_id': o.user_id,
                'book_id': o.book_id,
                'start_date': o.start_date,
                'due_date': o.due_date,
                'status': o.status,
            }
        except self.LoanModel.DoesNotExist:
            return None

    async def mark_returned(self, loan_id: str):
        self.LoanModel.objects.filter(loan_id=loan_id).update(status='returned')