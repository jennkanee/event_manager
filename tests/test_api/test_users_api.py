import pytest
from httpx import AsyncClient
from app.database import get_async_db
from app.main import app
from app.models.user_model import User
from app.utils.security import hash_password  # Import your FastAPI app

# Example of a test function using the async_client fixture
@pytest.mark.asyncio
async def test_create_user(async_client):
    form_data = {
        "username": "admin",
        "password": "secret",
    }
    # Login and get the access token
    token_response = await async_client.post("/token", data=form_data)
    access_token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Define user data for the test
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }

    # Send a POST request to create a user
    response = await async_client.post("/users/", json=user_data, headers=headers)

    # Asserts
    assert response.status_code == 201

# You can similarly refactor other test functions to use the async_client fixture
@pytest.mark.asyncio
async def test_retrieve_user(async_client, user, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"/users/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)

@pytest.mark.parametrize("field,value", [
   ("email", "updated@example.com"),
   ("full_name", "Updated Full Name"),
   ("bio", "Updated bio"),
])
@pytest.mark.asyncio
async def test_update_user_field(async_client, user, token, field, value):
   updated_data = {field: value}
   headers = {"Authorization": f"Bearer {token}"}
   response = await async_client.put(f"/users/{user.id}", json=updated_data, headers=headers)
   assert response.status_code == 200
   assert response.json()[field] == value

@pytest.mark.asyncio
async def test_update_user_email_name(async_client, user, token):
   updated_data = {
       "email": "updated@example.com",
       "full_name": "Updated Full Name",
   }
   headers = {"Authorization": f"Bearer {token}"}
   response = await async_client.put(f"/users/{user.id}", json=updated_data, headers=headers)
   assert response.status_code == 200
   assert response.json()["email"] == updated_data["email"]
   assert response.json()["full_name"] == updated_data["full_name"]

@pytest.mark.asyncio
async def test_update_user_email_bio(async_client, user, token):
   updated_data = {
       "email": "updated@example.com",
       "bio": "Updated bio"
   }
   headers = {"Authorization": f"Bearer {token}"}
   response = await async_client.put(f"/users/{user.id}", json=updated_data, headers=headers)
   assert response.status_code == 200
   for field, value in updated_data.items():
       assert response.json()[field] == value

@pytest.mark.asyncio
async def test_update_user_name_bio(async_client, user, token):
   updated_data = {
       "full_name": "Updated Full Name",
       "bio": "Updated bio"
   }
   headers = {"Authorization": f"Bearer {token}"}
   response = await async_client.put(f"/users/{user.id}", json=updated_data, headers=headers)
   assert response.status_code == 200
   for field, value in updated_data.items():
       assert response.json()[field] == value

@pytest.mark.asyncio
async def test_update_user_all_fields(async_client, user, token):
   updated_data = {
       "email": "updated@example.com",
       "full_name": "Updated Full Name",
       "bio": "Updated bio"
   }
   headers = {"Authorization": f"Bearer {token}"}
   response = await async_client.put(f"/users/{user.id}", json=updated_data, headers=headers)
   assert response.status_code == 200
   for field, value in updated_data.items():
       assert response.json()[field] == value

@pytest.mark.asyncio
async def test_delete_user(async_client, user, token):
    headers = {"Authorization": f"Bearer {token}"}
    delete_response = await async_client.delete(f"/users/{user.id}", headers=headers)
    assert delete_response.status_code == 204
    # Verify the user is deleted
    fetch_response = await async_client.get(f"/users/{user.id}", headers=headers)
    assert fetch_response.status_code == 404


@pytest.mark.asyncio
async def test_login_success(async_client, user):
    # Set up the test client for FastAPI application

    # Attempt to login with the test user
    response = await async_client.post("/login/", json={"username": user.username, "password": "MySuperPassword$1234"})
    
    # Check for successful login response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_create_user_duplicate_username(async_client, user):
    user_data = {
        "username": user.username,
        "email": "unique@example.com",
        "password": "AnotherPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "Username already exists" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_create_user_invalid_email(async_client):
    user_data = {
        "username": "uniqueuser",
        "email": "notanemail",
        "password": "ValidPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    login_data = {
        "username": "nonexistentuser",
        "password": "DoesNotMatter123!"
    }
    response = await async_client.post("/login/", json=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, user):
    login_data = {
        "username": user.username,
        "password": "IncorrectPassword123!"
    }
    response = await async_client.post("/login/", json=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_delete_user_does_not_exist(async_client, token):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID format
    headers = {"Authorization": f"Bearer {token}"}
    delete_response = await async_client.delete(f"/users/{non_existent_user_id}", headers=headers)
    assert delete_response.status_code == 404

