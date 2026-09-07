# Cycle Tracker - Django / DRF

TrackMate

## Live Demo

[Link if deployed]

## Tech Stack

- Frontend:
- Backend:
- Database:

## Features

- [Feature 1]
- [Feature 2]

## Project Setup

[Commands to run the project]

## Development Approach

### 1. Set Up Project

- Create the repo on github (with default _.gitignore_ for Python)
- Clone the repo on VS Code git clone https://github.com...git
- Create the projet structure with 2 folders: _backend_ and _frontend_

From _backend_:

- Create virtual environment `python -m venv venv` and activate it `source venv/Scripts/activate` (commands on bash)
- Install packages; one command line: `pip install django djangorestframework python-dotenv django-cors-headers gunicorn whitenoise dj-database-url "psycopg[binary]"`
  - **Django** -> to build the site's backend (pages, database, admin panel) - after installation, to see the version `django-admin --version`
  - **djangorestframework** -> lets Django return JSON data instead of HTML pages, so the TypeScript frontend can read it
  - **python-dotenv** -> loads secret values (API keys, database URL) from a .env file instead of writing them in the code
  - **psycopg[binary]** -> the modern translator between Django's Python code and the PostgreSQL database
  - **gunicorn** -> the actual server that runs the Django app once deployed on Scaleway (Django's own built-in server is dev-only)
  - **whitenoise** -> lets Django serve CSS/JS/image files itself in production, without needing a separate file server
  - **django-cors-headers** -> lets the backend accept requests from a different origin (like the frontend running on a different port), which browsers block by default
  - **dj-database-url** -> utility to easily parse the database URL provided by Scaleway
- Create the requirements file `pip freeze > requirements.txt`

### 2. Set Up Backend - Django

- From **backend** : start the django project `django-admin startproject core .` (_core_ = project name, the trailing `.` avoids an extra nested folder)
- Create Django App `python manage.py startapp <your_app_name>`
- In **settings.py**: replace the entire content with your **universal settings.py template** (pre-configured for DRF, CORS, WhiteNoise, Token Auth, and Hybrid SQLite/PostgreSQL database)
- In **settings.py** -> `INSTALLED_APPS`: add `<your_app_name>` to the list

### 3. Models

- **ERD, Design principles**: Only store raw, immutable user inputs in the database to keep the database light and accurate.
- In **models.py**, define the app's models (fields, relationships, and any custom logic like `save()` overrides)
- From **backend**: prepare the migration files `python manage.py makemigrations`, then apply them `python manage.py migrate`
  - _NOTE_: until the final database is configured in **settings.py**, Django uses SQLite by default
  - _NOTE_: re-run `makemigrations` + `migrate` every time you add or change a model field

### 4. Admin Panel

- In **admin.py**: register each model using `@admin.register(ModelName)` so they appear in the Django admin interface.
- From **backend**: create superuser `python manage.py createsuperuser` with credentials details (username and password)
- Run the local development server: `python manage.py runserver`
- Access the interface by appending `/admin` to the http address, to test creating, reading, and updating sample database entries manually.

### 5. Serializers

Serializers convert Python model objects into JSON (and validate JSON back into Python data) so the API can exchange data with a frontend.

From **backend/your_app_name**, create **serializers.py**.

- Import `serializers` from `rest_framework` and your models.
- Create a serializer class inheriting from `serializers.ModelSerializer`.
- Use a `Meta` class to define the target `model` and the list of `fields` to expose via JSON.
  - _NOTE_: calculated or automatic fields should be added to `read_only_fields` if they shouldn't be overridden by user inputs.

### 6. Views & Business Logic

Views handle incoming requests (GET, POST, PUT, DELETE) and use the serializer to read/write data accordingly.

From **backend/your_app_name**, in **views.py**:

- Import `viewsets` from `rest_framework`, the relevant models, and their serializers
- Create a ViewSet class inheriting from `viewsets.ModelViewSet`.
- Override `get_queryset()` to ensure users can only access their own data entries (`filter(user=self.request.user)`).
- Override `perform_create()` to automatically attach the currently logged-in user to the new database record upon creation (`serializer.save(user=self.request.user)`).

### 7. URLs

URLs map incoming requests to the right view. A router auto-generates all the standard routes (list, detail, create, update, delete) for each ViewSet.

From **backend/your_app_name**, create the file `urls.py`:

- At the top of the file, import `DefaultRouter` from `rest_framework.routers` and the relevant ViewSets
- Create a router instance, then `register()` each ViewSet under a URL prefix
- Set `urlpatterns = router.urls`
  - _NOTE_: If your ViewSet overrides `get_queryset()` instead of declaring a static `queryset` variable, you MUST provide a `basename` argument when registering the route (e.g., `router.register("prefix", ViewSet, basename="prefix")`), otherwise DRF will throw an AssertionError.

In **core/urls.py**:

- Import `include` alongside `path`
- Add a route delegating a prefix (e.g. `api/`) to the app's urls: `path('api/', include('<your_app_name>.urls'))`
