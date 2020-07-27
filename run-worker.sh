#!/bin/bash

set -e

# SSH_AUTH_SOCK to prevent CVAT from blocking when generating ssh keys
export SSH_AUTH_SOCK="fix"
command=/usr/bin/env python manage.py rqworker $*
