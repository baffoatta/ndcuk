"""
Pytest configuration and fixtures for NDC UK Backend tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@ndcuk.org",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "phone": "+447700900123",
        "address": "123 Test Street, London, UK",
        "date_of_birth": "1990-01-01"
    }

@pytest.fixture 
def sample_branch_data():
    """Sample branch data for tests"""
    return {
        "name": "Test Branch",
        "location": "Test Location", 
        "description": "Test branch for testing",
        "min_members": 20
    }

@pytest.fixture
def sample_role_assignment():
    """Sample role assignment for tests"""
    return {
        "user_id": "test-user-id",
        "role_id": "test-role-id",
        "chapter_id": "test-chapter-id",
        "notes": "Test assignment"
    }

@pytest.fixture
def mock_auth_headers():
    """Mock authentication headers"""
    return {
        "Authorization": "Bearer test-token"
    }