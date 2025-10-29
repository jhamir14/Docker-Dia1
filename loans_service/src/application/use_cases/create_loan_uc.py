from ...domain.services.loan_service import LoanService


def create_loan(loan_service: LoanService, user_id: str, book_id: str, days: int = 14):
    return loan_service.create(user_id, book_id, days)