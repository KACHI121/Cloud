# CampusHub Student CRUD

A small Flask and SQLite web application for demonstrating Create, Read, Update, and Delete operations in a cloud application development presentation.

## 1. Run locally

From this project directory:

```bash
cd ~/Cloud
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

To stop the application, press `Ctrl+C`.

## 2. Run the tests

```bash
source .venv/bin/activate
pytest -q
```

The tests check adding, editing, and deleting students.

## 3. Run with Docker

Build the image:

```bash
sudo docker build -t student-crud .
```

Start the container:

```bash
sudo docker run --name student-crud-container -p 5001:5000 student-crud
```

Open **http://localhost:5001**. Port `5001` on your computer connects to port `5000` inside the container.

Stop and remove the container:

```bash
sudo docker stop student-crud-container
sudo docker rm student-crud-container
```

If port 5000 is available, you can instead run:

```bash
sudo docker run --name student-crud-container -p 5000:5000 student-crud
```

Then open **http://localhost:5000**.

## 4. Docker troubleshooting

If Docker reports `permission denied`, either use `sudo` or add your user to the Docker group:

```bash
sudo usermod -aG docker "$USER"
```

Log out and log back in afterward. Then verify Docker access:

```bash
docker ps
```

If Docker reports `address already in use`, use a different host port such as `5001`:

```bash
sudo docker run --name student-crud-container -p 5001:5000 student-crud
```

To check what is using port 5000:

```bash
sudo lsof -i :5000
```

## 5. CRUD demonstration

1. Select **Add student** to create a record.
2. Use **Edit** to update a record.
3. Use **Delete** to remove a record.
4. Use the search box to find students.

The SQLite database is created automatically as `students.db` when the application starts.

## 6. Presentation workflow

```text
Write code → Test → Git/GitHub → Build Docker image → Run container → Access web app
```

The main files are:

- `app.py` — Flask application and CRUD routes
- `templates/` — HTML pages
- `static/style.css` — application styling
- `test_app.py` — automated tests
- `Dockerfile` — container build instructions
- `requirements.txt` — Python dependencies
