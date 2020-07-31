#!/bin/bash

set -e

printf "Starting daemon to rebuild frontend on changes\n"
( cd frontend && npm run-script dev & )

# make sure django serves static files and has verbose error pages
export DJANGO_DEBUG=true

printf "Starting opentpod\n"
# SSH_AUTH_SOCK to prevent CVAT from blocking when generating ssh keys
export SSH_AUTH_SOCK="fix"
/usr/bin/env python manage.py migrate && \
    /usr/bin/env python manage.py runserver 0.0.0.0:8000
