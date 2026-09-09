import os
import django
from pathlib import Path

# Set up the Django environment settings profile
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

def init_production():
    # 1. Automatically apply any pending database migrations on Scaleway PostgreSQL
    print("Running database migrations...")
    call_command('migrate', no_input=True)
    
    # 2. Safely create the production superuser if it does not exist yet
    User = get_user_model()
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    
    if password:
        if not User.objects.filter(username=username).exists():
            print(f"Creating superuser '{username}'...")
            User.objects.create_superuser(username=username, email=email, password=password)
            print("Superuser created successfully!")
        else:
            print(f"Superuser '{username}' already exists.")
    else:
        print("Skipping superuser creation: DJANGO_SUPERUSER_PASSWORD environment variable not set.")

    # 3. Automatically load cycles fixtures if the file exists
    fixture_file = Path(__file__).parent / 'cycles_fixture.json'
    if fixture_file.exists():
        print("Found local data fixture. Importing to production database...")
        try:
            call_command('loaddata', 'cycles_fixture.json')
            print("Data imported successfully!")
        except Exception as e:
            print(f"Error importing fixture: {e}")
    else:
        print("No data fixture found to import.")

if __name__ == '__main__':
    init_production()
