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

- In **models.py**, define the app's models (fields, relationships, and any custom logic like `save()` overrides)
- From **backend**: prepare the migration files `python manage.py makemigrations`, then apply them `python manage.py migrate`
  - _NOTE_: until the final database is configured in **settings.py**, Django uses SQLite by default
  - _NOTE_: re-run `makemigrations` + `migrate` every time you add or change a model field
- From **admin.py**: register each model so it appears in the admin panel (`@admin.register(...)`) — migrating alone isn't enough

### 4. Admin Panel

- From **backend**: create superuser credentials `python manage.py createsuperuser` with username and password
- To run the app: `python manage.py runserver`
- To access the admin panel, append `/admin` to the http address
- Testing phase: from the admin panel, create sample entries and check that fields (including calculated ones) display as expected

### 5. Create Heroku app and database

From **Heroku** Account:

- Create the app on Heroku
- Connect the app to GitHub repo
- On **Resources -> Add-on Services**: select the _heroku-postgresql_
- On **Settings -> Config Vars -> Reveal Config Vars**: get the _DATABASE_URL_ value

### 6. Connect backend to PostgreSQL

Back to VS Code, from **backend**:

- Create a file `.env` and add `DATABASE_URL=value copied from Heroku`
- Install `pip install dj-database-url`

In **settings.py**:

- Load environment variables at the top of the file:

```python
  import os
  from dotenv import load_dotenv
  import dj_database_url

  load_dotenv()
```

- Replace the default SQLite `DATABASES` config with:

```python
  DATABASES = {
      'default': dj_database_url.config(
          default=os.environ.get('DATABASE_URL')
      )
  }
```

- Run `python manage.py migrate` to apply migrations to PostgreSQL instead of SQLite
  - _NOTE_: if migrate fails with `ModuleNotFoundError: No module named 'psycopg2'` even though `pip show psycopg2-binary` confirms it's installed, the package may be corrupted (metadata present, actual code files missing). Fix: `pip uninstall psycopg2-binary` then reinstall `pip install psycopg2-binary`. Verify a package truly works with `python -c "import psycopg2"` rather than trusting `pip show` alone.

- After migration to PostgreSQL database, recreate a superuser and test (see above)

### 7. Serializers

Serializers convert Python model objects into JSON (and validate JSON back into Python data) so the API can exchange data with a frontend.

From **backend/tracking**, create the file `serializers.py`:

- At the top of the file, import `serializers` from `rest_framework` and the relevant models
- For each model, create a class inheriting from `serializers.ModelSerializer`, with a `Meta` class specifying `model` and `fields`
  - _NOTE_: fields not defined on the model (like the auto-generated `id`) can still be listed explicitly
  - _NOTE_: use `read_only_fields` in `Meta` for fields that are calculated automatically (e.g. in a model's `save()` method) — they'll still appear in responses but won't be required on creation

### 8. Views

Views handle incoming requests (GET, POST, PUT, DELETE) and use the serializer to read/write data accordingly.

From **backend/tracking**, in `views.py`:

- At the top of the file, import `viewsets` from `rest_framework`, the relevant models, and their serializers
- For each model, create a class inheriting from `viewsets.ModelViewSet`, with `queryset` (which objects to work with) and `serializer_class` (how to convert them to/from JSON)
  - _NOTE_: a `ModelViewSet` handles all CRUD operations (list, create, retrieve, update, delete) automatically — no need to write each one manually

### 9. URLs

URLs map incoming requests to the right view. A router auto-generates all the standard routes (list, detail, create, update, delete) for each ViewSet.

From **backend/tracking**, create the file `urls.py`:

- At the top of the file, import `DefaultRouter` from `rest_framework.routers` and the relevant ViewSets
- Create a router instance, then `register()` each ViewSet under a URL prefix (lowercase, plural, hyphen-separated — e.g. `food-items`)
- Set `urlpatterns = router.urls`

In **core/urls.py**:

- Import `include` alongside `path`
- Add a route delegating a prefix (e.g. `api/`) to the app's urls: `path('api/', include('tracking.urls'))`

In **settings.py**: add `'rest_framework'` to `INSTALLED_APPS` — required for the Browsable API interface to render correctly

### 10. Authentification

**Token-based authentication**: instead of Django's default open access, each request must include a token proving who's making it. A user logs in once (username + password) and receives a token, which is then attached to every subsequent request via an `Authorization` header.  
Unlike JWT, this token never expires automatically — simpler to reason about, no refresh logic needed.

- In **settings.py** : add `'rest_framework.authtoken'` to the existing `INSTALLED_APPS`
- Run migrations (creates the table that stores tokens)
- In **settings.py** : add the `REST_FRAMEWORK` dictionnary

```python
  REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
  }
```

- _NOTE_: `DEFAULT_PERMISSION_CLASSES: IsAuthenticated` makes every endpoint require a valid token by default, including the Browsable API

- In **core/urls.py**: import `obtain_auth_token` from `rest_framework.authtoken.views` and add a login route:

```python
path("api/login/", obtain_auth_token)
```

- _NOTE_: this view only accepts POST — visiting it in a browser (GET) returns a "Method not allowed" error, this is expected

### 11. Testing authentication

The Browsable API can't test POST endpoints without a form, and this one has none. We used **curl** in the terminal for testing purpose.  
_NOTE_: `curl` works from any folder — it just needs `python manage.py runserver` running in a separate terminal tab

- Log in and get a token:
  `curl -X POST http://127.0.0.1:8000/api/login/ -H "Content-Type: application/json" -d '{"username": "testuser", "password": "chosen_password"}'`

- Use the token to access a protected endpoint (GET):
  `curl http://127.0.0.1:8000/api/food-items/ -H "Authorization: Token *your_token_here*"`
  - _NOTE_: the header must include the word `Token` before the value, with a space

- Create an entry with the token (POST) — no need to include `user`, it's assigned automatically from the token via `perform_create`:
  `curl -X POST http://127.0.0.1:8000/api/food-logs/ -H "Authorization: Token *your_token_here*" -H "Content-Type: application/json" -d '{"date": "2026-07-20", "food_item": 1, "meal_type": "lunch", "portion_grams": 100}'`
  - _NOTE_: check the response includes the correct `user` id, matching the token's owner — confirms `perform_create` is working

### 12. Permissions

By default, an authenticated user can see and edit _everyone's_ data, not just their own — DRF only checks "are you logged in", not "does this belong to you". Two additions fix that, in each ViewSet:

In **views.py**:

- Add the method `perform_create`: automatically assigns the logged-in user to a new object, so the frontend never sends `user` manually and can't create entries on someone else's behalf.
- Add the method `get_queryset`: filters what a user can see/edit down to their own data, instead of returning everyone's (replaces the fixed `queryset` attribute)

In **urls.py**:

- Add to `router.register()` a `basename` argument as the ViewSet no longer has a fixed `queryset` attribute (replaced by `get_queryset`) — the router can't auto-detect the route name otherwise

### 13. Backend Deployment

In **settings.py**:

- Add `ALLOWED_HOSTS = ['app-url.herokuapp.com', 'localhost', '127.0.0.1']`
  - _NOTE_: Heroku may assign a URL different from the app name you chose — check the real URL after creating the app, don't assume it matches
- Add `whitenoise` to `MIDDLEWARE`, right after `SecurityMiddleware`
- Add `STATIC_ROOT = BASE_DIR / 'staticfiles'` below the existing `STATIC_URL`

From **backend**:

- Create a `Procfile` (no file extension) with:
  release: python manage.py migrate
  web: gunicorn core.wsgi

_NOTE_: `release` runs automatically after each deploy, before the new version goes live — keeps the database schema in sync with the code. Never use `makemigrations` here, only `migrate` — migrations should always be generated and tested locally first

- Ensure that **requirements.txt** is up to date:  
  `pip freeze > requirements.txt`

From **Heroku** Account:

- On **Settings -> Buildpacks -> Add Buildpack**:
  - Add the _Monorepo_ buildpack first `https://github.com/lstoll/heroku-buildpack-monorepo`
  - Add the _Python_ buildpack second  
    _NOTE_: order matters — monorepo must run first to reposition files before Python builds

- On **Settings -> Config Vars -> Reveal Congig Vars**: add a new key/value variable
  - Key `APP_BASE`
  - Value `backend`

- On **Deploy -> Manual Deploy**: select the branch _Main_ and click _Deploy Branch_
  _NOTE_: check the build log after each deploy — errors are usually clear (missing package in requirements.txt, missing config var, etc.) and safe to fix one at a time

### 14. Frontend Setup

_Vite_ is the build tool that replaced Create React App as the default choice for new React projects — faster dev server, faster builds, minimal config. It handles the frontend the way manage.py + Django handle the backend.

From **Frontend**:

- Check if Node.js is installed: `node -v`
- Install latest version of Vite: `npm create vite@latest .`
  - Select a framework: _React_
  - Select a variant: _TypeScript_
  - Which linter to use?: _ESLint_
  - Install with npm and start now?": _YES_

- To restart the dev server later: `npm run dev`

### 15. Frontend Structure

Three folders work together:

- **types/** describes the shape of data (frontend equivalent of models.py)
- **api/** contains functions that call the Django backend
- **components/** contains what the user sees and interacts with.

Files for Login (auth) example:

- In **types/auth.ts**: define what's sent to login (`LoginCredentials`) and what's received back (`LoginResponse`)
- In **api/auth.ts**: an async `login()` function that sends the credentials to `/api/login/` and returns the token
- In **components/LoginForm.tsx**: a form with username, password, and a submit button
- In **App.tsx**: import and display `LoginForm`

_NOTE_: exports work differently than in Python — anything meant to be used in another file needs `export` in front of it

_NOTE_: importing a type-only element (like an interface) needs `import type {...}`, not a plain `import {...}` — otherwise the browser tries to load something that no longer exists once compiled

### 16. Making the form interactive

React inputs don't hold their own value by default — the component must track it itself, using `useState`, and update it on every keystroke via `onChange`.

- `useState('')` returns a pair: the current value, and a function to update it (e.g. `const [username, setUsername] = useState('')`)
- `value={username}` displays whatever is currently stored
- `onChange={(e) => setUsername(e.target.value)}` updates the stored value on every keystroke — without it, the field stays frozen on its initial value

The form's `onSubmit` handler calls the `login()` API function with the current state values, instead of letting the form reload the page (`e.preventDefault()` blocks that default behavior).

### 17. CORS

Browsers block requests made from one origin (e.g. the frontend on `localhost:5173`) to a different one (e.g. the backend on `127.0.0.1:8000`), unless the server explicitly allows it — a security mechanism separate from Django's own `ALLOWED_HOSTS`.

In **settings.py**:

- Add `'corsheaders.middleware.CorsMiddleware'` to `MIDDLEWARE`, right after `SecurityMiddleware`
- Add `CORS_ALLOWED_ORIGINS = ['http://localhost:5173']` — lists which origins are allowed to call the API

_NOTE_: like `ALLOWED_HOSTS`, this will need updating once the frontend is deployed to a real URL

### 18. Storing the token

The token needs to survive a page refresh — otherwise the user would have to log in again every time. `localStorage` is the browser's built-in key/value storage that persists until explicitly cleared.

- In **api/token.ts**: two functions, `saveToken(token)` (stores it) and `getToken()` (retrieves it, or `null` if none exists)
- In **LoginForm.tsx**: after a successful login, call `saveToken(result.token)` to store the received token

_NOTE_: `getToken(): string | null` is a _union type_ — it tells TypeScript the result might be a real string, or `null` if nothing was ever stored (e.g. no one has logged in yet). This forces checking before using the value elsewhere, instead of risking a crash.

On dev tools we should see a `token` key with the stored value:
![Token in Local Storage](docs/screenshots/local_storage.png)

## Refactoring & Decisions

[Technical choices, why]

## Lessons Learned

[What we should do differently and why]

## Areas for Improvement

[Future functionnalities, improvements]

# cycle-tracker
