from ...domain.services.loan_service import LoanService


def return_loan(loan_service: LoanService, loan_id: str):
    return loan_service.return_loan(loan_id)