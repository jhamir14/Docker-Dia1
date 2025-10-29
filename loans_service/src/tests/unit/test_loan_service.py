import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date, timedelta
from src.domain.services.loan_service import LoanDomainService


class TestLoanDomainService:
    @pytest.fixture
    def mock_dependencies(self):
        """Setup mock dependencies for LoanDomainService"""
        users_mock = AsyncMock()
        books_mock = AsyncMock()
        loans_mock = AsyncMock()
        clock_mock = Mock()
        uuid_mock = Mock()
        
        # Default successful responses
        users_mock.get_user.return_value = {"id": "u1", "status": "active"}
        users_mock.get_user_active_loans_count.return_value = 1
        books_mock.get_book.return_value = {"id": "b1", "status": "available"}
        clock_mock.today.return_value = date(2025, 10, 29)
        uuid_mock.new.return_value = "loan-123"
        
        return {
            "users": users_mock,
            "books": books_mock,
            "loans": loans_mock,
            "clock": clock_mock,
            "uuid": uuid_mock
        }

    @pytest.fixture
    def loan_service(self, mock_dependencies):
        """Create LoanDomainService with mocked dependencies"""
        return LoanDomainService(**mock_dependencies)

    @pytest.mark.asyncio
    async def test_create_loan_success(self, loan_service, mock_dependencies):
        """Test successful loan creation"""
        result = await loan_service.create_loan("u1", "b1", 7)
        
        # Verify all external calls were made
        mock_dependencies["users"].get_user.assert_called_once_with("u1")
        mock_dependencies["users"].get_user_active_loans_count.assert_called_once_with("u1")
        mock_dependencies["books"].get_book.assert_called_once_with("b1")
        mock_dependencies["books"].mark_loaned.assert_called_once_with("b1")
        mock_dependencies["loans"].save.assert_called_once()
        
        # Verify loan structure
        assert result["loan_id"] == "loan-123"
        assert result["user_id"] == "u1"
        assert result["book_id"] == "b1"
        assert result["start_date"] == date(2025, 10, 29)
        assert result["due_date"] == date(2025, 11, 5)  # 7 days later
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_loan_invalid_days(self, loan_service):
        """Test loan creation with invalid days"""
        with pytest.raises(ValueError, match="Duration must be 1..15 days"):
            await loan_service.create_loan("u1", "b1", 20)

    @pytest.mark.asyncio
    async def test_create_loan_inactive_user(self, loan_service, mock_dependencies):
        """Test loan creation with inactive user"""
        mock_dependencies["users"].get_user.return_value = {"id": "u1", "status": "suspended"}
        
        with pytest.raises(ValueError, match="User is not active"):
            await loan_service.create_loan("u1", "b1", 7)

    @pytest.mark.asyncio
    async def test_create_loan_too_many_loans(self, loan_service, mock_dependencies):
        """Test loan creation when user has too many active loans"""
        mock_dependencies["users"].get_user_active_loans_count.return_value = 3
        
        with pytest.raises(ValueError, match="User has too many active loans"):
            await loan_service.create_loan("u1", "b1", 7)

    @pytest.mark.asyncio
    async def test_create_loan_book_not_available(self, loan_service, mock_dependencies):
        """Test loan creation with unavailable book"""
        mock_dependencies["books"].get_book.return_value = {"id": "b1", "status": "loaned"}
        
        with pytest.raises(ValueError, match="Book is not available"):
            await loan_service.create_loan("u1", "b1", 7)

    @pytest.mark.asyncio
    async def test_return_loan_success(self, loan_service, mock_dependencies):
        """Test successful loan return"""
        mock_dependencies["loans"].get.return_value = {
            "loan_id": "loan-123",
            "user_id": "u1",
            "book_id": "b1",
            "status": "active"
        }
        
        result = await loan_service.return_loan("loan-123")
        
        # Verify external calls
        mock_dependencies["loans"].get.assert_called_once_with("loan-123")
        mock_dependencies["loans"].mark_returned.assert_called_once_with("loan-123")
        mock_dependencies["books"].mark_returned.assert_called_once_with("b1")
        
        # Verify result
        assert result["loan_id"] == "loan-123"
        assert result["status"] == "returned"

    @pytest.mark.asyncio
    async def test_return_loan_not_found(self, loan_service, mock_dependencies):
        """Test returning non-existent loan"""
        mock_dependencies["loans"].get.return_value = None
        
        with pytest.raises(ValueError, match="Loan not found"):
            await loan_service.return_loan("nonexistent")

    @pytest.mark.asyncio
    async def test_return_loan_already_returned(self, loan_service, mock_dependencies):
        """Test returning already returned loan"""
        mock_dependencies["loans"].get.return_value = {
            "loan_id": "loan-123",
            "user_id": "u1",
            "book_id": "b1",
            "status": "returned"
        }
        
        with pytest.raises(ValueError, match="Loan not active"):
            await loan_service.return_loan("loan-123")

    @pytest.mark.asyncio
    async def test_create_loan_edge_case_minimum_days(self, loan_service, mock_dependencies):
        """Test loan creation with minimum valid days"""
        result = await loan_service.create_loan("u1", "b1", 1)
        
        assert result["due_date"] == date(2025, 10, 30)  # 1 day later

    @pytest.mark.asyncio
    async def test_create_loan_edge_case_maximum_days(self, loan_service, mock_dependencies):
        """Test loan creation with maximum valid days"""
        result = await loan_service.create_loan("u1", "b1", 15)
        
        assert result["due_date"] == date(2025, 11, 13)  # 15 days later

    @pytest.mark.asyncio
    async def test_create_loan_user_at_loan_limit(self, loan_service, mock_dependencies):
        """Test loan creation when user is at loan limit (2 active loans)"""
        mock_dependencies["users"].get_user_active_loans_count.return_value = 2
        
        # Should succeed as limit is 3
        result = await loan_service.create_loan("u1", "b1", 7)
        assert result["status"] == "active"