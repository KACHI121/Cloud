# CampusHub Student CRUD

A small Flask web application for demonstrating Create, Read, Update, and Delete operations in a cloud application development presentation. It uses SQLite locally and PostgreSQL when `DATABASE_URL` is set.

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

The local SQLite database is created automatically as `students.db` when the application starts. A cloud PostgreSQL database starts with an empty student list.

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

## 7. Deploy with Neon PostgreSQL and Render

1. Go to [Neon](https://console.neon.tech/), create a project, and choose a region near your Render service. On the project dashboard, use **Connect** to copy the PostgreSQL connection string. Keep the full string, including `sslmode=require`, private.
2. Push the current application changes to the GitHub repository. This project already has an `origin` remote; check it with `git remote -v`. From `~/Cloud`, use:

   ```bash
   git add app.py test_app.py requirements.txt Dockerfile gunicorn.conf.py .dockerignore README.md
   git commit -m "Prepare student app for PostgreSQL and Render"
   git push origin main
   ```

3. At [Render](https://dashboard.render.com/), choose **New → Web Service**, select the GitHub repository, choose the `main` branch, and set **Language** to **Docker**. Leave the Dockerfile path as `./Dockerfile`. Choose a plan that fits your demo; **Free** works for a classroom presentation.
4. In Render's environment settings, add:

   | Key | Value |
   | --- | --- |
   | `DATABASE_URL` | The full Neon connection string from step 1 |
   | `SECRET_KEY` | A long random value from `python3 -c 'import secrets; print(secrets.token_hex(32))'` |

   Do not put either value in a committed file. The application accepts Neon's normal `postgresql://...` URL and converts it internally for the installed PostgreSQL driver.
5. Set the Render health check path to `/health` if the option is shown, then create the web service. Render builds the Docker image and starts Gunicorn. No custom build or start command is needed.
6. After Render reports **Live**, open the assigned `https://...onrender.com` URL. Add a student, refresh the page, edit the student, then delete it. Use Render's **Logs** tab if the service does not start.

The `students` table is created automatically on first startup. Existing data in the local `students.db` file is **not** copied to Neon. For a demo, add fresh student records through the website.

Render's free web service sleeps after 15 minutes of inactivity, so open the site shortly before presenting. Student records stay in Neon while the service sleeps. This app has no login; anyone who has the public URL can edit or delete its demo records, so use fictional student details only.
