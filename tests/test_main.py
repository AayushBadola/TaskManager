import pytest
from fastapi.testclient import TestClient
from typing import Generator
from task_manager_api.main import app
from task_manager_api import database

@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    database.reset_db_for_testing()
    yield TestClient(app)

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Task Manager API"}

def test_create_task(client: TestClient):
    response = client.post(
        "/tasks/",
        json={"title": "Test Task 1", "description": "Test Description 1"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task 1"
    assert data["description"] == "Test Description 1"
    assert data["completed"] is False
    assert "id" in data
    assert data["id"] == 1

def test_create_multiple_tasks(client: TestClient):
    client.post("/tasks/", json={"title": "Task A", "description": "Desc A"})
    response = client.post("/tasks/", json={"title": "Task B", "description": "Desc B"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task B"
    assert data["id"] == 2

def test_read_tasks_empty(client: TestClient):
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert response.json() == []

def test_read_tasks_populated(client: TestClient):
    client.post("/tasks/", json={"title": "Task 1"})
    client.post("/tasks/", json={"title": "Task 2"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"

def test_read_single_task(client: TestClient):
    create_response = client.post("/tasks/", json={"title": "Read Me"})
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Read Me"
    assert data["id"] == task_id

def test_read_nonexistent_task(client: TestClient):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"message": "Task with id 999 not found"}

def test_update_task(client: TestClient):
    create_response = client.post("/tasks/", json={"title": "Update Me", "description": "Initial Desc"})
    task_id = create_response.json()["id"]
    update_payload = {"title": "Updated Title", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Initial Desc"
    assert data["completed"] is True
    assert data["id"] == task_id

def test_update_task_partial(client: TestClient):
    create_response = client.post("/tasks/", json={"title": "Partial Update", "description": "Desc"})
    task_id = create_response.json()["id"]
    update_payload = {"description": "New Description"}
    response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Partial Update"
    assert data["description"] == "New Description"
    assert data["completed"] is False
    assert data["id"] == task_id

def test_update_nonexistent_task(client: TestClient):
    response = client.put("/tasks/999", json={"title": "Doesn't Matter"})
    assert response.status_code == 404
    assert response.json() == {"message": "Task with id 999 not found"}

def test_delete_task(client: TestClient):
    create_response = client.post("/tasks/", json={"title": "Delete Me"})
    task_id = create_response.json()["id"]
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    get_response_after_delete = client.get(f"/tasks/{task_id}")
    assert get_response_after_delete.status_code == 404

def test_delete_nonexistent_task(client: TestClient):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"message": "Task with id 999 not found"}

def test_invalid_input_create(client: TestClient):
    response = client.post("/tasks/", json={"description": "Missing title"})
    assert response.status_code == 422
    long_title = "a" * 101
    response = client.post("/tasks/", json={"title": long_title, "description": "Long title"})
    assert response.status_code == 422

def test_invalid_input_update(client: TestClient):
    create_response = client.post("/tasks/", json={"title": "Valid Task"})
    task_id = create_response.json()["id"]
    long_title = "a" * 101
    response = client.put(f"/tasks/{task_id}", json={"title": long_title})
    assert response.status_code == 422
    response = client.put(f"/tasks/{task_id}", json={"completed": "not-a-boolean"})
    assert response.status_code == 422

