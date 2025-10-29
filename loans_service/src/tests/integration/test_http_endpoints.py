import os
import pytest
import pytest_asyncio
import httpx
import asyncio
from datetime import datetime


@pytest.fixture
def base_url():
    """Base URL for the loans service.
    Uses SERVICE_BASE_URL if set; defaults to http://localhost:8001.
    When running tests inside a compose container, set SERVICE_BASE_URL=http://loans_service:8001
    """
    return os.environ.get("SERVICE_BASE_URL", "http://localhost:8001")


@pytest_asyncio.fixture
async def http_client():
    """HTTP client for making requests"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint(http_client, base_url):
    """Test health endpoint is accessible"""
    response = await http_client.get(f"{base_url}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "healthy")


@pytest.mark.asyncio
async def test_create_loan_success(http_client, base_url):
    """Test successful loan creation with valid data"""
    loan_data = {
        "user_id": "user123",
        "book_id": "book456",
        "days": 7
    }
    
    response = await http_client.post(
        f"{base_url}/api/loans",
        json=loan_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "loan_id" in data
    assert data["user_id"] == loan_data["user_id"]
    assert data["book_id"] == loan_data["book_id"]
    assert data["status"] == "active"
    
    return data["loan_id"]  # Return for cleanup or further tests


@pytest.mark.asyncio
async def test_create_loan_invalid_days(http_client, base_url):
    """Test loan creation fails with invalid days (> 15)"""
    loan_data = {
        "user_id": "user123",
        "book_id": "book456",
        "days": 20  # Exceeds MAX_DAYS (15)
    }
    
    response = await http_client.post(
        f"{base_url}/api/loans",
        json=loan_data
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "days" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_loan_missing_fields(http_client, base_url):
    """Test loan creation fails with missing required fields"""
    loan_data = {
        "user_id": "user123",
        # Missing book_id and days
    }
    
    response = await http_client.post(
        f"{base_url}/api/loans",
        json=loan_data
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_return_loan_not_found(http_client, base_url):
    """Test returning a non-existent loan"""
    fake_loan_id = "non-existent-loan-id"
    
    response = await http_client.post(
        f"{base_url}/api/loans/{fake_loan_id}/return"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_debug_endpoint(http_client, base_url):
    """Test debug endpoint returns loan information"""
    response = await http_client.get(f"{base_url}/api/debug/loans")
    
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "ids" in data
    assert isinstance(data["count"], int)
    assert isinstance(data["ids"], list)


@pytest.mark.asyncio
async def test_full_loan_lifecycle(http_client, base_url):
    """Test complete loan lifecycle: create -> return"""
    # Step 1: Create a loan
    loan_data = {
        "user_id": "lifecycle_user",
        "book_id": "lifecycle_book",
        "days": 5
    }
    
    create_response = await http_client.post(
        f"{base_url}/api/loans",
        json=loan_data
    )
    
    assert create_response.status_code == 200
    loan = create_response.json()
    loan_id = loan["loan_id"]
    
    # Step 2: Verify loan exists in debug
    debug_response = await http_client.get(f"{base_url}/api/debug/loans")
    debug_data = debug_response.json()
    assert loan_id in debug_data["ids"]
    
    # Step 3: Return the loan
    return_response = await http_client.post(
        f"{base_url}/api/loans/{loan_id}/return"
    )
    
    assert return_response.status_code == 200
    return_data = return_response.json()
    assert return_data["message"] == "Loan returned successfully"
    assert return_data["loan_id"] == loan_id


@pytest.mark.asyncio
async def test_concurrent_loan_creation(http_client, base_url):
    """Test concurrent loan creation doesn't cause issues"""
    loan_requests = []
    
    for i in range(3):
        loan_data = {
            "user_id": f"concurrent_user_{i}",
            "book_id": f"concurrent_book_{i}",
            "days": 7
        }
        loan_requests.append(
            http_client.post(f"{base_url}/api/loans", json=loan_data)
        )
    
    # Execute all requests concurrently
    responses = await asyncio.gather(*loan_requests, return_exceptions=True)
    
    # All should succeed (using different users/books)
    for response in responses:
        assert not isinstance(response, Exception)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_endpoint(http_client, base_url):
    """Test OpenAPI documentation is available"""
    response = await http_client.get(f"{base_url}/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data
    
    # Verify our endpoints are documented
    paths = data["paths"]
    assert "/api/loans" in paths
    assert "/health" in paths


if __name__ == "__main__":
    # Instructions for running these tests:
    # 1. Start the services: docker compose up -d
    # 2. Run tests: pytest src/tests/integration/ -v
    print("Integration tests for loans service HTTP endpoints")
    print("Make sure to start services with: docker compose up -d")