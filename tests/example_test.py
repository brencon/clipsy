"""
Example Python Test File

This file demonstrates testing patterns for Python projects
using pytest. Delete or modify for your project.

Run with: pytest or pytest tests/
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import Optional

# ============================================
# Example: Testing Pure Functions
# ============================================


# Functions to test (normally imported from src/)
def add(a: int, b: int) -> int:
    return a + b


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Division by zero")
    return a / b


class TestMathUtilities:
    """Test suite for math utility functions."""

    def test_add_positive_numbers(self):
        """Should add two positive numbers."""
        # Arrange
        a, b = 2, 3

        # Act
        result = add(a, b)

        # Assert
        assert result == 5

    def test_add_negative_numbers(self):
        """Should handle negative numbers."""
        assert add(-1, -2) == -3
        assert add(-1, 2) == 1

    def test_add_zero(self):
        """Should handle zero."""
        assert add(0, 5) == 5
        assert add(5, 0) == 5

    def test_divide_numbers(self):
        """Should divide two numbers."""
        assert divide(10, 2) == 5.0

    def test_divide_by_zero_raises(self):
        """Should raise ValueError on division by zero."""
        with pytest.raises(ValueError, match="Division by zero"):
            divide(10, 0)


# ============================================
# Example: Testing with Fixtures
# ============================================


@dataclass
class User:
    id: str
    name: str
    email: str


@pytest.fixture
def sample_user() -> User:
    """Fixture providing a sample user for tests."""
    return User(id="123", name="Test User", email="test@example.com")


@pytest.fixture
def user_list() -> list[User]:
    """Fixture providing multiple users."""
    return [
        User(id="1", name="Alice", email="alice@example.com"),
        User(id="2", name="Bob", email="bob@example.com"),
        User(id="3", name="Charlie", email="charlie@example.com"),
    ]


class TestUserFixtures:
    """Tests demonstrating fixture usage."""

    def test_user_has_email(self, sample_user: User):
        """Should have valid email."""
        assert "@" in sample_user.email

    def test_user_list_count(self, user_list: list[User]):
        """Should have correct number of users."""
        assert len(user_list) == 3


# ============================================
# Example: Testing Async Functions
# ============================================


async def fetch_user(user_id: str) -> Optional[User]:
    """Simulated async API call."""
    # In real code, this would call an API
    if user_id == "not-found":
        return None
    return User(id=user_id, name="Fetched User", email="fetched@example.com")


async def create_user(name: str, email: str) -> User:
    """Simulated async user creation."""
    return User(id="new-id", name=name, email=email)


class TestAsyncFunctions:
    """Tests for async functions."""

    @pytest.mark.asyncio
    async def test_fetch_user_success(self):
        """Should fetch user by ID."""
        user = await fetch_user("123")

        assert user is not None
        assert user.id == "123"
        assert user.name == "Fetched User"

    @pytest.mark.asyncio
    async def test_fetch_user_not_found(self):
        """Should return None for non-existent user."""
        user = await fetch_user("not-found")

        assert user is None

    @pytest.mark.asyncio
    async def test_create_user(self):
        """Should create new user."""
        user = await create_user("New User", "new@example.com")

        assert user.name == "New User"
        assert user.email == "new@example.com"


# ============================================
# Example: Testing with Mocks
# ============================================


class EmailService:
    """Service for sending emails."""

    def send(self, to: str, subject: str, body: str) -> bool:
        # In real code, this would send an email
        raise NotImplementedError("Use mock in tests")


class UserService:
    """Service for user operations."""

    def __init__(self, email_service: EmailService):
        self.email_service = email_service

    def register_user(self, name: str, email: str) -> User:
        """Register a new user and send welcome email."""
        user = User(id="new-id", name=name, email=email)
        self.email_service.send(
            to=email, subject="Welcome!", body=f"Hello {name}, welcome to our platform!"
        )
        return user


class TestUserServiceWithMocks:
    """Tests demonstrating mock usage."""

    def test_register_user_sends_email(self):
        """Should send welcome email on registration."""
        # Arrange
        mock_email_service = Mock(spec=EmailService)
        mock_email_service.send.return_value = True
        service = UserService(mock_email_service)

        # Act
        user = service.register_user("Alice", "alice@example.com")

        # Assert
        assert user.name == "Alice"
        mock_email_service.send.assert_called_once_with(
            to="alice@example.com",
            subject="Welcome!",
            body="Hello Alice, welcome to our platform!",
        )


# ============================================
# Example: Parametrized Tests
# ============================================


@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("hello", "HELLO"),
        ("World", "WORLD"),
        ("PyTest", "PYTEST"),
        ("", ""),
    ],
)
def test_uppercase(input_value: str, expected: str):
    """Should convert string to uppercase."""
    assert input_value.upper() == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
    ],
)
def test_add_parametrized(a: int, b: int, expected: int):
    """Should add numbers correctly (parametrized)."""
    assert add(a, b) == expected


# ============================================
# Example: Testing Exceptions
# ============================================


def validate_email(email: str) -> str:
    """Validate and normalize email."""
    if not email:
        raise ValueError("Email cannot be empty")
    if "@" not in email:
        raise ValueError("Invalid email format")
    return email.lower().strip()


class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email(self):
        """Should accept valid email."""
        assert validate_email("Test@Example.com") == "test@example.com"

    def test_empty_email_raises(self):
        """Should raise for empty email."""
        with pytest.raises(ValueError) as exc_info:
            validate_email("")
        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_format_raises(self):
        """Should raise for invalid format."""
        with pytest.raises(ValueError) as exc_info:
            validate_email("not-an-email")
        assert "Invalid email format" in str(exc_info.value)


# ============================================
# Example: Testing with Context Managers
# ============================================


@pytest.fixture
def temp_file(tmp_path):
    """Fixture providing a temporary file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path


def test_read_file(temp_file):
    """Should read file content."""
    content = temp_file.read_text()
    assert content == "test content"


# ============================================
# Example: Marking Tests
# ============================================


@pytest.mark.slow
def test_slow_operation():
    """This test is marked as slow (skip with: pytest -m 'not slow')."""
    import time

    time.sleep(0.1)  # Simulating slow operation
    assert True


@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """This test is skipped."""
    pass


@pytest.mark.skipif(
    condition=True,  # Replace with actual condition
    reason="Skipping in CI environment",
)
def test_local_only():
    """This test only runs locally."""
    pass
