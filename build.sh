#!/usr/bin/env bash
# exit on error
set -o errexit

# ✅ Force correct Python version
echo "Forcing Python 3.11 installation..."
pyenv install -s 3.11.9
pyenv global 3.11.9
python -m pip install --upgrade pip setuptools wheel

# ✅ Install dependencies and migrate
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
