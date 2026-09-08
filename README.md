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
- Create the projet structure with 2 folders: **backend** and **frontend**

From **backend**:

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

From **backend**:

- Start the django project `django-admin startproject core .` (_core_ = project name, the trailing `.` avoids an extra nested folder)
- Create Django App `python manage.py startapp <your_app_name>`
- Create your local environmental file: create a `.env` file at the root of the **backend** folder. Add `DEBUG=True`, then copy the automatically generated `SECRET_KEY` from the fresh `core/settings.py` and paste it here.
- Overwrite **core/settings.py**: replace the entire content of the generated file with your **universal settings.py template** (pre-configured for DRF, CORS, WhiteNoise, Token Auth, and Hybrid SQLite/PostgreSQL database).
- In **settings.py** -> `INSTALLED_APPS`: add `<your_app_name>` to the list
  - _NOTE_: In `core/settings.py`, the `REST_FRAMEWORK` configuration is wrapped inside an `if DEBUG:` block.
    - In **Local Development** (`DEBUG=True`), permissions are automatically set to `AllowAny` to bypass token restrictions and easily audit calculations directly inside your browser.
    - In **Production** (`DEBUG=False`), strict `TokenAuthentication` and `IsAuthenticated` permissions are enforced to secure the endpoints.

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

From **backend/your_app_name**, create **serializers.py**

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

From **backend/your_app_name**, create **urls.py**

- At the top of the file, import `DefaultRouter` from `rest_framework.routers` and the relevant ViewSets
- Create a router instance, then `register()` each ViewSet under a URL prefix
- Set `urlpatterns = router.urls`
  - _NOTE_: If your ViewSet overrides `get_queryset()` instead of declaring a static `queryset` variable, you MUST provide a `basename` argument when registering the route (e.g., `router.register("prefix", ViewSet, basename="prefix")`), otherwise DRF will throw an AssertionError.

In **core/urls.py**:

- Import `include` alongside `path`
- Add a route delegating a prefix (e.g. `api/`) to the app's urls: `path('api/', include('<your_app_name>.urls'))`

### 8. Production Deployment (Scaleway Serverless)

From **backend**, create 2 files: `Dockerfile` and a `.dockerignore`. For the content of each file, use the template.

Follow these steps to deploy the backend architecture once local development is finalized:

#### A. Database Provisioning (PostgreSQL)

- In Scaleway Console, go to **Databases** (left menu) -> **Serverless SQL**
- Click **Create Database** and configure:
  - **Region**: `Paris (fr-par)`
  - **Default engine version**: `PostgreSQL-16` (or latest)
  - **Configure database autoscaling**: optimize your budget by selecting **Minimum vCPU** to `0` (for scale-to-zero € when inactive) and **Maximum vCPU** to `1` (strict budget ceiling)
  - **Database Instance name**: `<your_app_name>-db`
- Click **Create Database**
- Once ready, click **Connect** -> **Generate API Key** (set expiration to 1 Year).
- Copy the complete **Connection String** (`postgresql://...`) and save it securely for step B.

#### B. Production Namespace & Environment Variables

- Go to **Serverless Compute** (left menu) -> **Containers**
- Click **Create a Namespace** (the secure global folder for your apps) and configure:
  - **Namespace name**: `portfolio-backend` (or a generic studio name)
  - **Region**: `Paris (fr-par)`
- Open **Advanced Options** to access the **Environment Variables** section. Add these 3 variables without any quotes or brackets:
  - `SECRET_KEY` = (Your production Django secret key available in .env)
  - `DEBUG` = `False` (exact casing matters — `settings.py` does a strict string comparison)
  - `DATABASE_URL` = (the connection string from step A)
- Click **Create namespace and add container**

#### C. Deploying the Quickstart Container Shell

- Click **Deploy a Container** and select **Quickstart image** (Simple Hello World container)
- Configure the container options:
  - **Container name**: `<your_app_name>-api`
  - **Resources**, optimize your budget by selecting the minimum values:
    - **CPU**: `100 m vCPU` (or lowest available)
    - **Memory**: `256 MB` (perfect balance to run Django without crashing)
- Under **Autoscaling**, strict-bind your scale thresholds:
  - **minimum**: `1` (keeps 1 instance active for instant recruiter responses)
  - **maximum**: `1` (prevents duplication costs)
- Click **Deploy container**
- Once the status icon turns **Green (Ready)**, go to the **Overview** and open the public **Container endpoint** to verify it responds in the browser

#### D. GitHub Repository Secrets

- On Scaleway, retrieve two values:
  - **Container ID**: Serverless → Containers → your container → **Overview** → `Container ID`
  - **Secret Key** (reusable across all projects in the same Scaleway Organization): Console → top-right menu → **IAM & API keys** → **API keys** → select the key named **github-actions-deploy** (create it once via **Generate API key** if it doesn't exist yet, then reuse it for every future project)

- On GitHub, go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, and add:
  - `SCW_SECRET_KEY` = (the Secret Key above) — authenticates every Scaleway API call
  - `SCW_CONTAINER_ID` = (the Container ID above) — target of the deployment

#### E. Container Registry Setup

- Go to **Containers** (left menu) → **Container Registry**.
- A namespace is usually created automatically the first time you push an image, but you can also create one manually: **Create namespace**, name it to match your Serverless Containers namespace (e.g. `<studio-name>-backend`), region `Paris (fr-par)`.
- On **Overview**, copy the **Registry endpoint**: `rg.fr-par.scw.cloud/<namespace-name>/<your-app-name>-api`

#### F. GitHub Actions Workflow

From the project root (same level as folders backend and fronted), create a new structure with 2 folders and a file `.github/workflows/deploy.yml`
For the content of **deploy.yml**, use the template and adjust the `IMAGE` path to match your project:  
`env:`  
 `IMAGE: rg.fr-par.scw.cloud/<registry-namespace>/<container-name>:${{ github.sha }}`

Replace `<registry-namespace>` with your Container Registry namespace (step E) and `<container-name>` with your Serverless container's name (step C). Everything else in the workflow stays identical across projects

The workflow builds the Docker image, pushes it to the Registry, then calls the Scaleway API to redeploy the container with the new image. It runs automatically on every push to `main`

#### H. Verifying the Deployment

- On GitHub, check the **Actions** tab: the workflow run should complete with a green checkmark
- On Scaleway, go to the container's **Overview** tab: status should read **Ready** (it briefly shows **Updating** during redeploy)
- Visit the public **Endpoint URL** + `/admin/` in a browser
- Since `DEBUG=False` enforces `TokenAuthentication` + `IsAuthenticated`, API endpoints won't respond to a plain browser visit. Test them with `curl` or Postman, passing `Authorization: Token <your-token>`
