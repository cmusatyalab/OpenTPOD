---
description: Explains how to setup and administer an OpenTPOD server.
---

# Guide to Setup the Server

## Background

### OpenTPOD Architecture

![OpenTPOD Architecture](tpod-arch.png)

### What is in this repository

* config: Django website configuration files.
* requirements: Conda and pip requirement files for development and deployment.
* opentpod: Main Django module for OpenTPOD.
* cvat: a symlink to third_party/cvat. Integrated third party annotation tool CVAT. This symlink is needed here for it to be treated as a Django module as well.
* keys: a keys directory with an empty module to make CVAT behave nicely.
* nginx: nginx configuration files.
* docker-compose.yml/docker-compose.override.yml: Docker compose file for development.
* docker-compose.prod.yml: Docker compose file for production deployment.
* Dockerfile: Dockerfile to build the openTPOD container image.
* dotenv.example: Example environment variables to set as a ".env" file.
* manage.py: Django manage.py file to run Django default functionalities.
* third_party: git submodules referencing CVAT releases.
* frontend: React-based frontend. Created using the create-react-app.
* run-development.sh: Script to rebuild frontend React code and Django
  server in development mode.
* run-frontend.sh: Script to collect React and Django static files together into
  static directory and run a production server.
* run-worker.sh: Script to run individual Django-RQ workers.
* docs: documentation

## Installation

First, clone this repository with submodules.

```bash
git clone --recurse-submodules https://github.com/cmusatyalab/OpenTPOD.git
```

Then, configure the configuration variables, mostly setting passwords by copying
and editing the `dotenv.example` file to `.env`.

```
$ cp dotenv.example .env
$ vi .env
```

The server can be started in either **deployment** or **debug** configurations.

### Deployment

This configuration runs everything inside containers.

```bash
$ # make sure you have copied and modified dotenv.example to .env
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

The server may take a few minutes to start up as it pulls the current docker
image and initializes it's state. After the server is up, indicated by log
message "listening at..", create an administrative account with the following
command.

```bash
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec opentpod bash
opentpod# python ./manage.py createsuperuser
```

Now, you can access the website with the admin account at **http://localhost:20000/**.

### Debugging Backend inside Containers (Recommended)

This runs the django development server inside of the container, but uses
the local source.

```bash
$ # make sure you have copied and modified dotenv.example to .env
$ docker-compose up --build -d
$ # access opentpod container
```

At this point you can modify the frontend or backend code as you see fit and
it should automatically recompile in case an update doesn't seem to get picked
up, or when the django/npm daemons have stopped working, rerun 'docker-compose
up -d --build' to restart. It will then rebuild the container, picking up any
missed changes.

```bash
$ # to see logging from the container either drop the '-d' or
$ docker-compose logs -f opentpod
$ # to poke around inside the container
$ docker-compose exec opentpod bash
```

NOTE: (developing the production environment hack). If you want to promote the
current 'development' container to production status you can tag the
opentpod:latest image as opentpod:stable and then the production deployment
will deploy it instead of pulling down the existing stable container.

```bash
$ # make sure opentpod:latest matches the current development tree
$ docker-compose build
$ # tag and redeploy production
$ docker tag opentpod:latest opentpod:stable
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Debugging Backend and Frontend without Containers

```bash
$ # install all the dependencies, follow Dockerfile
$ # run backend server
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py collectstatic
$ python manage.py rqworker default low tensorboard &
$ python manage.py runserver 0.0.0.0:8000
$
$ # launch npm dev server for serving frontend code
$ cd frontend
$ npm install
$ npm run-script watch
```

## Uninstallation

```bash
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
$ # or if you want to remove all your data as well, use
$ docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v
```


## Administration

#### Create User Accounts

Users can create accounts by following the *sign up* link on the login page.
However, newly created accounts do not have access to the website functionalities
until an administrator explicitly gives the account permission.
See [below](####Grant-users-permission-to-access-the-system) for granting users permissions to access the website.

#### Grant users permission to access the system

1. Go to /admin/auth/user and login with an administrator account.
2. Click on the user name you want to modify.
3. In "Permissions >> Groups", choose the appropriate permission group for the user. Normal users should be assigned "user" group while administrator accounts should be assigned "admin" group.
