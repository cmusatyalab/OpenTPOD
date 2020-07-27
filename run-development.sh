#!/bin/bash -l

set -e

test -n "$DATABASE_URL" || echo "Missing DATABASE_URL" && exit 0

# Update conda environment
conda env update -f requirements/environment.yml --prune

# rebuild frontend
( cd frontend && npm install && npm run-script build )

# populate www directory
mkdir -p www
rm -rf www/*

# collect CVAT static files we don't need database or redis cache for that.
( DATABASE_URL="sqlite:///" REDIS_URL="" REDIS_CACHE_URL="" \
  python manage.py collectstatic --noinput --clear )

# install nodejs static files
cp -r frontend/build/* www/

printf "Static files collected!\n"

printf "Starting processes\n"
supervisord -n -c supervisord/dev.conf
