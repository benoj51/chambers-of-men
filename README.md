# Chambers of Men

**Awaken. Equip. Deploy.**

A Django web platform and CRM for Chambers of Men - a faith-based movement restoring men through structured leadership, discipleship, and strategic deployment.

## Tech Stack

- **Backend:** Django 5.1 / Python 3.12
- **Database:** PostgreSQL (SQLite for local dev)
- **Server:** Gunicorn + WhiteNoise
- **Deployment:** Railway (Docker)

## Project Structure

```
chambers-of-men/
├── chambers/          # Django project settings and root URL config
├── website/           # Public-facing website app (views, URLs)
├── crm/               # CRM app (models, admin dashboard)
├── templates/         # HTML templates
│   └── website/       # Website page templates
├── static/            # Static assets (CSS, JS, images)
├── Dockerfile         # Production Docker build
├── railway.json       # Railway deployment config
├── Procfile           # Process file for Railway
├── requirements.txt   # Python dependencies
└── manage.py          # Django management script
```

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/chambers-of-men.git
cd chambers-of-men
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and set:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (for CRM admin access)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Visit:
- **Website:** http://localhost:8000
- **CRM Admin:** http://localhost:8000/admin

## Deploying to Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit - Chambers of Men platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/chambers-of-men.git
git push -u origin main
```

### 2. Create Railway project

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub Repo"**
4. Connect your GitHub account and select the `chambers-of-men` repo

### 3. Add a PostgreSQL database

1. In your Railway project, click **"+ New"**
2. Select **"Database" > "Add PostgreSQL"**
3. Railway will automatically set the `DATABASE_URL` environment variable

### 4. Set environment variables

In your Railway service settings, add these variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate a strong key: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `your-app.up.railway.app` |

Railway automatically provides:
- `PORT` - the port to bind to
- `DATABASE_URL` - PostgreSQL connection string
- `RAILWAY_PUBLIC_DOMAIN` - your app's public domain

### 5. Deploy

Railway will automatically detect the Dockerfile, build, and deploy. The first deployment will:
- Build the Docker image
- Run database migrations
- Collect static files
- Start the Gunicorn server

### 6. Create admin user

In the Railway service, go to **Settings > Deploy > Run Command** or use the Railway CLI:

```bash
railway run python manage.py createsuperuser
```

## CRM Features

The admin dashboard at `/admin` provides:

- **Members** - full member directory with status tracking, role assignment, and church membership details
- **Chambers** - organisational units by city/region with assigned leaders
- **Iron Circles** - small group management (max 5 members per circle)
- **Events** - event creation and attendance tracking
- **Blog Posts** - content management with categories (Doctrine, Testimony, Devotional, Update, Teaching)
- **Contact Submissions** - website signup form entries with one-click member creation

## Website Pages

- `/` - Home (full landing page)
- `/about/` - About the movement
- `/events/` - Upcoming events
- `/blog/` - Blog and teachings
- `/contact/` - Contact form
- `/signup/` - Join form (AJAX endpoint)

## Taglines

*"Keep climbing, brother."*
*"You're not alone, brother."*
