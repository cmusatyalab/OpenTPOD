#!/bin/bash

set -e

printf "Starting daemon to rebuild frontend on changes\n"
( cd frontend && npm run-script dev & )

# make sure django serves static files and has verbose error pages
export DJANGO_DEBUG=true

printf "Starting opentpod\n"
# SSH_AUTH_SOCK to prevent CVAT from blocking when generating ssh keys
export SSH_AUTH_SOCK="fix"

/usr/bin/env python manage.py migrate
/usr/bin/env python manage.py runserver 0.0.0.0:8000

## for debugging segfaults (runserver exits with 245/-11)
## the sleep allows us to exec a shell in the container and poke around
#/usr/bin/env python -X faulthandler manage.py runserver --noreload 0.0.0.0:8000 || sleep 3600
