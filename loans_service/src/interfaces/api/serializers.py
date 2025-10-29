from pydantic import BaseModel, Field


class CreateLoanRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    book_id: str = Field(..., min_length=1)
    days: int = Field(default=14, ge=1, le=15)


class LoanResponse(BaseModel):
    loan_id: str
    user_id: str
    book_id: str
    start_date: str
    due_date: str
    status: str