from fastapi import APIRouter, HTTPException
from ..api.serializers import CreateLoanRequest, LoanResponse
from ...infrastructure.repositories.memory_store import LOANS
from .container import get_service
from ...infrastructure.logging.json_logger import logger


router = APIRouter()


def build_service():
    return get_service()


@router.post("/api/loans", response_model=LoanResponse)
async def create_loan(payload: CreateLoanRequest):
    logger.info("API: Create loan request received", extra={
        "user_id": payload.user_id,
        "book_id": payload.book_id,
        "days": payload.days
    })
    
    service = build_service()
    try:
        loan = await service.create_loan(payload.user_id, payload.book_id, payload.days)
        
        logger.info("API: Create loan request successful", extra={
            "user_id": payload.user_id,
            "book_id": payload.book_id,
            "loan_id": loan.get("loan_id")
        })
        
    except ValueError as e:
        logger.warning("API: Create loan request failed", extra={
            "user_id": payload.user_id,
            "book_id": payload.book_id,
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("API: Create loan request error", extra={
            "user_id": payload.user_id,
            "book_id": payload.book_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Internal server error")
    return LoanResponse(
        loan_id=loan['loan_id'],
        user_id=loan['user_id'],
        book_id=loan['book_id'],
        start_date=loan['start_date'].isoformat(),
        due_date=loan['due_date'].isoformat(),
        status=loan['status'],
    )


@router.post("/api/loans/{loan_id}/return")
async def return_loan(loan_id: str):
    logger.info("API: Return loan request received", extra={"loan_id": loan_id})
    
    service = build_service()
    try:
        result = await service.return_loan(loan_id)
        
        logger.info("API: Return loan request successful", extra={
            "loan_id": loan_id,
            "user_id": result.get("user_id"),
            "book_id": result.get("book_id")
        })
        
        return {"message": "Loan returned successfully", "loan_id": loan_id}
    except ValueError as e:
        logger.warning("API: Return loan request failed", extra={
            "loan_id": loan_id,
            "error": str(e)
        })
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("API: Return loan request error", extra={
            "loan_id": loan_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/debug/loans")
async def debug_loans():
    logger.info("API: Debug loans request received")
    result = {
        "count": len(LOANS),
        "ids": list(LOANS.keys()),
    }
    logger.info("API: Debug loans request successful", extra={"loans_count": len(LOANS)})
    return result