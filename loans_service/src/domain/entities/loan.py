from dataclasses import dataclass
from datetime import date


@dataclass
class Loan:
    loan_id: str
    user_id: str
    book_id: str
    start_date: date
    due_date: date
    status: str  # "active" | "returned"