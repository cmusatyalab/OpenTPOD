#!/bin/bash

set -e

# because we're running from a prebuilt container, we only have to
# make sure to re-populate the www-static volume which is shared with
# an nginx container
mkdir -p static
rm -rf static/*

# collect static files, we don't need the database, redis or cache for that.
( DATABASE_URL="sqlite:///" REDIS_URL="" CACHE_URL="" \
  python manage.py collectstatic --noinput --clear )

printf "Static files collected!\n"
printf "nginx should serve DIR: $(readlink -f static)\n"

# SSH_AUTH_SOCK to prevent CVAT from blocking when generating ssh keys
export SSH_AUTH_SOCK="fix"
/usr/bin/env python manage.py migrate && \
    /usr/bin/env gunicorn config.wsgi:application --log-file - --log-level debug -b :8000
