---
description: Explains how to setup OpenTPOD server.
---

# Installation

The server can be started in either **debug** or **deployment** configurations.

### Debug

This would create infrastructures inside containers while running the django
development server natively on the host.

Opened port:
    * 0.0.0.0:3001: react server port, specified in .envrc
    * localhost:5000: django development app server

```bash
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

