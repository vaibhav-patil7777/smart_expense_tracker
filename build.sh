
#!/usr/bin/env bash
set -o errexit

# Install deps (Render already does pip install -r requirements.txt,
# but safe to add any custom steps)
pip install -r requirements.txt

# Migrate DB and collect static files (no input)
python manage.py migrate --noinput
python manage.py collectstatic --noinput
