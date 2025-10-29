from datetime import timedelta

MAX_ACTIVE_LOANS = 3
MAX_DAYS = 15

def validate_max_days(days: int):
    if days < 1 or days > MAX_DAYS:
        raise ValueError(f"Duration must be 1..{MAX_DAYS} days")

def validate_user_active(user_status: str):
    if user_status != "active":
        raise ValueError("User is not active")

def validate_user_loans_count(count: int):
    if count >= MAX_ACTIVE_LOANS:
        raise ValueError("User has too many active loans")

def validate_book_available(book_status: str):
    if book_status != "available":
        raise ValueError("Book is not available")