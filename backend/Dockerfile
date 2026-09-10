# --- Stage 1: Base build stage ---
# Source: https://www.docker.com/blog/how-to-dockerize-django-app/
FROM python:3.13-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Production stage ---
FROM python:3.13-slim

# Create a non-root user and the app directory, then hand ownership to that user
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy application code, owned by the non-root user
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Collect static files so whitenoise can serve them in production
# Source: https://docs.djangoproject.com/en/stable/howto/static-files/deployment/
RUN python manage.py collectstatic --noinput

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8080

# Start the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "core.wsgi:application"]