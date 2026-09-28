import pytest
from app import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.DATABASE", tmp_path / "test.db")
    with app.test_client() as client:
        with app.app_context():
            from app import init_db
            init_db()
        yield client


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
