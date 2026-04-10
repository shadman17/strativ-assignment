# Weather Forecast API

This is a **Django + PostgreSQL + Redis + Celery** backend that provides APIs for:

- Viewing top 10 districts
- Getting travel recommendations based on weather and air quality

---

## 1) What you need before starting

Please install these tools first:

- **Git** (to download the project)
- **Docker Desktop** (includes Docker + Docker Compose)

> You do **not** need to install Python/PostgreSQL/Redis manually when using Docker.

---

## 2) Download the project

Open Terminal (Mac/Linux) or PowerShell (Windows) and run:

```bash
git clone https://github.com/shadman17/strativ-assignment.git
cd strativ-assignment
```

---

## 3) Create the `.env` file

Inside the project folder, create a file named **`.env`** and paste this:

```env
SECRET_KEY=django-insecure-6d9wjs7nq-ms@d03pju
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0
BASE_URL=http://localhost:8005/

# Postgres
DB_NAME=weather_db
DB_USER=weather_user
DB_PASSWORD=weather_password
DB_HOST=db
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CELERY_BEAT_HOUR=18
CELERY_BEAT_MINUTE=7
```

---

## 4) Start the project

Run this command in the project folder:

```bash
docker compose up --build
```

First startup may take a few minutes. The app will automatically:

- wait for the database
- run migrations
- import district data
- start the Django server

When ready, open:

- Django admin: [http://localhost:8005/admin/](http://localhost:8005/admin/)
- Celery Flower dashboard: [http://localhost:5555](http://localhost:5555)

---

## 5) Create a login user

In a **new terminal window**, run this command:

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to create username/password.

---

## 6) Get API token

Use your new username/password to get auth token:

**Terminal (Mac/Linux)**
```bash
curl -X POST http://localhost:8005/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'
```

**Powershell (Windows)**
```bash
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/auth/token/" `
  -Method POST `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'
```

You will get a token like:

```json
{"token":"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
```

Copy this token.

---

## 7) Test the APIs

Replace `YOUR_TOKEN` with your real token.

### A) Top 10 districts

**Terminal (Mac/Linux)**
```bash
curl -X GET http://localhost:8005/api/v1/districts/top-10-districts/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Powershell (Windows)**
```bash
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/districts/top-10-districts/" `
  -Method GET `
  -Headers @{ "Authorization" = "Token YOUR_TOKEN" }
```
> Do not miss Token keyword! Also, make sure you ran Celery Periodic Task at least once! Celery Periodic Task setup is mentioned below!

### B) Travel recommendation

**Terminal (Mac/Linux)**
```bash
curl -X POST http://localhost:8005/api/v1/travel/recommendation/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "latitude": 23.8103,
    "longitude": 90.4125,
    "destination_district_id": 1,
    "travel_date": "2026-04-15"
  }'
```

**Powershell (Windows)**
```bash
Invoke-RestMethod -Uri "http://localhost:8005/api/v1/travel/recommendation/" `
  -Method POST `
  -Headers @{ 
    "Content-Type"  = "application/json"
    "Authorization" = "Token YOUR_TOKEN"
  } `
  -Body '{
    "latitude": 23.8103,
    "longitude": 90.4125,
    "destination_district_id": 1,
    "travel_date": "2026-04-15"
  }'
```
> Do not miss Token keyword! Also, make sure you ran Celery Periodic Task at least once! Celery Periodic Task setup is mentioned below!

---

## 8) Stop the project

Press `Ctrl + C` where Docker is running, then run:

```bash
docker compose down
```

If you also want to remove saved database/cache volumes:

```bash
docker compose down -v
```
> Caution: It will remove your database!
---

## 9) How to set Celery Beat time (hour and minute)

This project runs scheduled background tasks daily using **Celery Beat**.

Suppose you want the task to run at 6:30 PM.

You can set the schedule in **either** of these ways:

### Option A (Recommended): Set in `.env`

In your `.env` file, set:

```env
CELERY_BEAT_HOUR=18
CELERY_BEAT_MINUTE=30
```

- `CELERY_BEAT_HOUR` = hour in 24-hour format (`0` to `23`)
- `CELERY_BEAT_MINUTE` = minute (`0` to `59`)

Example:
- `18:30` means daily at **6:30 PM**
- `06:30` means daily at **6:30 AM**

After changing these values, restart containers:

```bash
docker compose down
docker compose up --build
```

### Option B: Set defaults in `settings.py`

If you are comfortable editing code, open:

- `project_weatherforecast/settings.py`

and update the default values used when `.env` is missing:

```python
CELERY_BEAT_HOUR = int(os.getenv("CELERY_BEAT_HOUR", "18"))
CELERY_BEAT_MINUTE = int(os.getenv("CELERY_BEAT_MINUTE", "30"))
```

> `.env` values override `settings.py` defaults.  
> So for most users, changing `.env` is enough.
After changing these values, restart containers:

```bash
docker compose down
docker compose up --build
```

## 10) Common issues

- **Port already in use (8005/5555/6379)**
  - Close other apps using those ports, then retry.
- **Docker not running**
  - Start Docker Desktop first.
- **Token auth failing**
  - Recheck username/password and ensure header is exactly:
    - `Authorization: Token YOUR_TOKEN`

---

## 11) Quick restart next time

After first setup, if the containers are running, you usually only need:

```bash
docker compose up
```