#!/usr/bin/env bash
# build.sh
set -o errexit  # stop build on error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
