import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.user_schemas import UserBase, UserCreate, UserUpdate, UserResponse, UserListResponse, LoginRequest

# Fixtures for common test data
@pytest.fixture
def user_base_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "full_name": "John H. Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "unique-id-string",
        "username": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"username": "john_doe_123", "password": "SecurePassword123!"}

# Helper function to create a UserBase instance and assert the username
def create_and_assert_user_base(username, user_base_data):
    user_base_data["username"] = username
    user = UserBase(**user_base_data)
    assert user.username == username

# Tests for UserBase
def test_user_base_valid(user_base_data):
    user = UserBase(**user_base_data)
    assert user.email == user_base_data["email"]

# Tests for UserCreate
def test_user_create_valid(user_create_data):
    user = UserCreate(**user_create_data)
    assert user.password == user_create_data["password"]

# Tests for UserUpdate
def test_user_update_partial(user_update_data):
    partial_data = {"email": user_update_data["email"]}
    user_update = UserUpdate(**partial_data)
    assert user_update.email == partial_data["email"]

# Tests for UserResponse
def test_user_response_datetime(user_response_data):
    user = UserResponse(**user_response_data)
    assert user.last_login_at == user_response_data["last_login_at"]
    assert user.created_at == user_response_data["created_at"]
    assert user.updated_at == user_response_data["updated_at"]

# Tests for LoginRequest
def test_login_request_valid(login_request_data):
    login = LoginRequest(**login_request_data)
    assert login.username == login_request_data["username"]
    assert login.password == login_request_data["password"]

# Parametrized tests for valid usernames
@pytest.mark.parametrize("username", [
    "a" * 50,  # Exactly 50 characters (assuming it's the maximum allowed length)
    "username_with_underscore",
    "username-with-hyphens",
    "username_with_numbers_123",
    "USERNAME_WITH_UPPERCASE",
    "username_with_mixed_Case",
    "username_with_trailing_underscore_",
    "_username_with_leading_underscore",
])
def test_user_base_username_valid(username, user_base_data):
    create_and_assert_user_base(username, user_base_data)

# Fixture for invalid usernames with special characters
special_characters = "!@#$%^&*()+={}[]|\\:;'\"<>,./?`~"
invalid_usernames_with_special_chars = [
    f"username_with_special_char{char}" for char in special_characters
]

# Parametrized tests for invalid usernames
@pytest.mark.parametrize("username", [
    "a" * 51,  # One character over the maximum allowed length
    " username_with_leading_space",
    "username_with_trailing_space ",
    "username with spaces",
    "username.with.dots",
    "a",  # Username too short (assuming minimum length is 2)
] + invalid_usernames_with_special_chars)
def test_user_base_username_invalid(username, user_base_data):
    user_base_data["username"] = username
    with pytest.raises(ValidationError):
        UserBase(**user_base_data)

# Tests for password validation
@pytest.mark.parametrize("password", [
    "Str0ngP@ssw0rd!",  # Strong password with mix of uppercase, lowercase, numbers, and special characters
    "G00dPassword!"
])
def test_user_create_password_valid(password, user_create_data):
    user_create_data["password"] = password
    user = UserCreate(**user_create_data)
    assert user.password == password

@pytest.mark.parametrize("password", [
    "a" * 11,  # Password shorter than minimum allowed length
    "password",  # Password without uppercase letters
    "PASSWORD",  # Password without lowercase letters
    "Password",  # Password without numbers
    "Password123",  # Password without special characters
    "p@ssw0rd",  # Password shorter than minimum allowed length, even with complexity
])
def test_user_create_password_invalid(password, user_create_data):
    user_create_data["password"] = password
    with pytest.raises(ValidationError):
        UserCreate(**user_create_data)
