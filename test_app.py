import pytest

from app import create_app, database_uri


@pytest.fixture()
def client(tmp_path):
    app = create_app(f"sqlite:///{tmp_path / 'test.db'}")
    app.config["TESTING"] = True
    return app.test_client()


def test_create_and_list_student(client):
    response = client.post("/students/new", data={"name": "Test Student", "email": "test@example.com", "course": "Computing", "year": "2"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test Student" in response.data


def test_update_student(client):
    client.post("/students/new", data={"name": "Old Name", "email": "old@example.com", "course": "Computing", "year": "1"})
    response = client.post("/students/1/edit", data={"name": "New Name", "email": "new@example.com", "course": "Design", "year": "3"}, follow_redirects=True)
    assert b"New Name" in response.data
    assert b"Old Name" not in response.data


def test_delete_student(client):
    client.post("/students/new", data={"name": "Delete Me", "email": "delete@example.com", "course": "Math", "year": "1"})
    response = client.post("/students/1/delete", follow_redirects=True)
    assert b"Delete Me" not in response.data


def test_duplicate_email_keeps_database_usable(client):
    data = {"name": "First", "email": "same@example.com", "course": "Math", "year": "1"}
    client.post("/students/new", data=data)
    response = client.post("/students/new", data=data, follow_redirects=True)
    assert b"already registered" in response.data
    assert b"First" in client.get("/").data


def test_postgres_url_uses_psycopg():
    assert database_uri("postgresql://user:pass@host/db?sslmode=require") == "postgresql+psycopg://user:pass@host/db?sslmode=require"


def test_health(client):
    assert client.get("/health").data == b"ok"
