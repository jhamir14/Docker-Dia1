import pytest
from src.domain.rules.validators import (
    validate_max_days,
    validate_user_active,
    validate_user_loans_count,
    validate_book_available,
    MAX_DAYS,
    MAX_ACTIVE_LOANS
)


class TestValidateMaxDays:
    def test_validate_max_days_ok(self):
        """Test valid days within range"""
        validate_max_days(5)
        validate_max_days(1)
        validate_max_days(MAX_DAYS)

    def test_validate_max_days_error_too_high(self):
        """Test days exceeding maximum"""
        with pytest.raises(ValueError, match=f"Duration must be 1..{MAX_DAYS} days"):
            validate_max_days(20)

    def test_validate_max_days_error_zero(self):
        """Test zero days"""
        with pytest.raises(ValueError, match=f"Duration must be 1..{MAX_DAYS} days"):
            validate_max_days(0)

    def test_validate_max_days_error_negative(self):
        """Test negative days"""
        with pytest.raises(ValueError, match=f"Duration must be 1..{MAX_DAYS} days"):
            validate_max_days(-1)

    def test_validate_max_days_edge_cases(self):
        """Test edge cases at boundaries"""
        validate_max_days(1)  # minimum valid
        validate_max_days(15)  # maximum valid
        
        with pytest.raises(ValueError):
            validate_max_days(16)  # just over maximum


class TestValidateUserActive:
    def test_user_active_ok(self):
        """Test active user passes validation"""
        validate_user_active("active")

    def test_user_inactive_error(self):
        """Test inactive user raises error"""
        with pytest.raises(ValueError, match="User is not active"):
            validate_user_active("inactive")

    def test_user_suspended_error(self):
        """Test suspended user raises error"""
        with pytest.raises(ValueError, match="User is not active"):
            validate_user_active("suspended")

    def test_user_blocked_error(self):
        """Test blocked user raises error"""
        with pytest.raises(ValueError, match="User is not active"):
            validate_user_active("blocked")


class TestValidateUserLoansCount:
    def test_loans_count_ok(self):
        """Test valid loan counts"""
        validate_user_loans_count(0)
        validate_user_loans_count(1)
        validate_user_loans_count(2)

    def test_loans_count_at_limit_error(self):
        """Test loan count at maximum limit"""
        with pytest.raises(ValueError, match="User has too many active loans"):
            validate_user_loans_count(MAX_ACTIVE_LOANS)

    def test_loans_count_over_limit_error(self):
        """Test loan count over maximum limit"""
        with pytest.raises(ValueError, match="User has too many active loans"):
            validate_user_loans_count(MAX_ACTIVE_LOANS + 1)
            validate_user_loans_count(10)


class TestValidateBookAvailable:
    def test_book_available_ok(self):
        """Test available book passes validation"""
        validate_book_available("available")

    def test_book_loaned_error(self):
        """Test loaned book raises error"""
        with pytest.raises(ValueError, match="Book is not available"):
            validate_book_available("loaned")

    def test_book_reserved_error(self):
        """Test reserved book raises error"""
        with pytest.raises(ValueError, match="Book is not available"):
            validate_book_available("reserved")

    def test_book_maintenance_error(self):
        """Test book in maintenance raises error"""
        with pytest.raises(ValueError, match="Book is not available"):
            validate_book_available("maintenance")

    def test_book_lost_error(self):
        """Test lost book raises error"""
        with pytest.raises(ValueError, match="Book is not available"):
            validate_book_available("lost")


class TestValidatorsIntegration:
    """Integration tests combining multiple validators"""
    
    def test_valid_loan_scenario(self):
        """Test a complete valid loan scenario"""
        validate_max_days(7)
        validate_user_active("active")
        validate_user_loans_count(1)
        validate_book_available("available")

    def test_invalid_loan_scenarios(self):
        """Test various invalid loan scenarios"""
        # Invalid days
        with pytest.raises(ValueError):
            validate_max_days(30)
        
        # Inactive user
        with pytest.raises(ValueError):
            validate_user_active("suspended")
        
        # Too many loans
        with pytest.raises(ValueError):
            validate_user_loans_count(5)
        
        # Unavailable book
        with pytest.raises(ValueError):
            validate_book_available("loaned")