from datetime import timedelta
from ..ports.loans_repo import LoansPort
from ..ports.users_repo import UsersPort
from ..ports.books_repo import BooksPort
from ..ports.clock import Clock
from ..ports.uuid_gen import UUIDGen
from ..rules.validators import (
    validate_max_days,
    validate_user_active,
    validate_user_loans_count,
    validate_book_available,
)
from ...infrastructure.logging.json_logger import logger


class LoanDomainService:
    def __init__(self, users: UsersPort, books: BooksPort, loans: LoansPort, clock: Clock, uuidgen: UUIDGen):
        self.users = users
        self.books = books
        self.loans = loans
        self.clock = clock
        self.uuidgen = uuidgen

    async def create_loan(self, user_id: str, book_id: str, days: int):
        logger.info("Creating loan", extra={
            "user_id": user_id,
            "book_id": book_id,
            "days": days
        })
        
        try:
            validate_max_days(days)
            logger.info("Max days validation passed", extra={"user_id": user_id, "book_id": book_id, "days": days})
            
            user = await self.users.get_user(user_id)
            validate_user_active(user['status'])
            logger.info("User active validation passed", extra={"user_id": user_id, "user_status": user['status']})
            
            count = await self.users.get_user_active_loans_count(user_id)
            validate_user_loans_count(count)
            logger.info("User loans count validation passed", extra={
                "user_id": user_id,
                "active_loans_count": count
            })
            
            book = await self.books.get_book(book_id)
            validate_book_available(book['status'])
            logger.info("Book availability validation passed", extra={"book_id": book_id, "book_status": book['status']})

            loan_id = self.uuidgen.new()
            start = self.clock.today()
            due = start + timedelta(days=days)

            loan = {
                'loan_id': loan_id,
                'user_id': user_id,
                'book_id': book_id,
                'start_date': start,
                'due_date': due,
                'status': 'active'
            }
            await self.loans.save(loan)
            await self.books.mark_loaned(book_id)
            
            logger.info("Loan created successfully", extra={
                "user_id": user_id,
                "book_id": book_id,
                "loan_id": loan_id,
                "due_date": due.isoformat()
            })
            
            return loan
            
        except Exception as e:
            logger.error("Failed to create loan", extra={
                "user_id": user_id,
                "book_id": book_id,
                "error": str(e)
            })
            raise

    async def return_loan(self, loan_id: str):
        logger.info("Returning loan", extra={"loan_id": loan_id})
        
        try:
            loan = await self.loans.get(loan_id)
            if not loan:
                logger.warning("Loan not found", extra={"loan_id": loan_id})
                raise ValueError("Loan not found")
            if loan['status'] != 'active':
                logger.warning("Loan is not active", extra={
                    "loan_id": loan_id,
                    "current_status": loan['status']
                })
                raise ValueError("Loan is not active")
            
            loan['status'] = 'returned'
            loan['return_date'] = self.clock.today()
            await self.loans.save(loan)
            await self.books.mark_available(loan['book_id'])
            
            logger.info("Loan returned successfully", extra={
                "loan_id": loan_id,
                "user_id": loan['user_id'],
                "book_id": loan['book_id'],
                "return_date": loan['return_date'].isoformat()
            })
            
            return loan
            
        except Exception as e:
            logger.error("Failed to return loan", extra={
                "loan_id": loan_id,
                "error": str(e)
            })
            raise