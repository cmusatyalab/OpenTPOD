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

### Backend Debugging Inside Contaienrs (Recommended)

This would create infrastructures inside containers while running the django
development server natively on the host.

Opened port:
    * 0.0.0.0:3001: react server port, specified in .envrc
    * localhost:5000: django development app server

```bash
$ # copy and modify .envrc.example to .envrc.prod
$ source .envrc.prod
$ docker-compose -f docker-compose.debug.yml build
$ docker-compose -f docker-compose.debug.yml up
$ # access opentpod container
$ docker-compose -f docker-compose.debug.yml exec opentpod /bin/bash
$ # inside opentpod container
$ conda activate opentpod-env
$ # modify the code as you see fit
$ # to launch the server and testing
$ python manage.py migrate
$ python manage.py rqworker default low tensorboard
$ python manage.py runserver 0.0.0.0:8000
```

### Debugging Backend and Frontend Natively 
```
$ # install all the dependencies
$ # run backend server
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py collectstatic
$ python manage.py rqworker default low tensorboard
$ python manage.py runserver 0.0.0.0:5000
$
$ # launch npm dev server for serving frontend code
$ cd frontend
$ npm i
$ npm run-script watch
```

## Administration

#### Give users permission to access the system

1. Go to /admin/auth/user and login with an administrator account.
2. Click on the user name you want to modify.
3. In "Permissions >> Groups", choose the appropriate permission group for the user. Normal users should be assigned "user" group while administrator accounts should be assigned "admin" group.
