# 1. Use a lightweight Linux image with Python 3.11 pre-installed
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and force real-time log flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the entire Django application source code into the container
COPY . /app/

# 6. Collect static files so whitenoise can serve them in production
RUN python manage.py collectstatic --noinput

# 7. Production command to launch Gunicorn (Scaleway serverless requires port 8080)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080"]