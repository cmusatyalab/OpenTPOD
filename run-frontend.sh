#!/bin/bash

set -e

# populate www directory, should be a volume shared with an nginx container
mkdir -p www
rm -rf www/*

# collect CVAT static files we don't need database or redis cache for that.
( DATABASE_URL="sqlite:///" REDIS_URL="" CACHE_URL="" \
  python manage.py collectstatic --noinput --clear )

# install nodejs static files
cp -r frontend/build/* www/

printf "Static files collected!\n"
printf "nginx should serve DIR: $(readlink -f www)\n"

# SSH_AUTH_SOCK to prevent CVAT from blocking when generating ssh keys
export SSH_AUTH_SOCK="fix"
/usr/bin/env python manage.py migrate && \
    /usr/bin/env gunicorn config.wsgi:application --log-file - --log-level debug -b :8000
