---
description: Explains how to setup OpenTPOD server.
---

# Guide to Setup the Server

## What is in this repository

* [config](../config): Django website configuration files.
* requirements: Conda and pip requirement files for development and deployment.
* opentpod: Main Django module for OpenTPOD.
* cvat: a symlink to third_party/cvat. Integrated third party annotation tool CVAT. This symlink is needed here for it to be treated as a Django module as well.
* keys: a keys directory with an empty module to make CVAT behave nicely.
* supervisord: supervisord configurations to launch the server.
* nginx: nginx configuration files.
* docker-compose.yml: debug Docker compose file.
* docker-compose.prod.yml: Docker compose file for deployment.
* Dockerfile: Dockerfile to build the openTPOD container image.
* .envrc.example: Example environment variables to set.
* manage.py: Django manage.py file to run Django default functionalities.
* third_party: git submodules referencing CVAT releases.
* frontend: React-based frontend. Created using the create-react-app.
* build_frontend.sh: Script to build frontend React code and collect Django
  static files together into static and www directory for serving.
* docs: Gitbook Documentation

## Installation

The server can be started in either **debug** or **deployment** configurations.

### Debug

This would create infrastructures inside containers while running the django
development server natively on the host.

Opened port:
    * 0.0.0.0:3001: react server port, specified in .envrc
    * localhost:5000: django development app server

```bash
$ # copy and modify .envrc.example to .envrc
$ conda env create -f requirements/environment-dev.yml
$ conda activate opentpod-env
$ ln -s third_party/cvat/cvat cvat
$ source .envrc
$ docker-compose up
$ supervisord -n -c supervisord/dev.conf
```

### Deployment

This configurations runs everything inside containers.

```bash
$ # copy and modify .envrc.example to .envrc.prod
$ source .envrc.prod
$ docker-compose -f docker-compose.prod.yml build
$ docker-compose -f docker-compose.prod.yml up
```

Opened port:
    * 0.0.0.0:20000: nginx web server, serving static files
    * 127.0.0.1:20001: gunicorn app server

### Without Using supervisord
```
$ # old instructions
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py collectstatic
$ python manage.py rqworker default low
$ python manage.py runserver 0.0.0.0:5000
$ cd frontend
$ npm i
$ npm run-script watch
```

