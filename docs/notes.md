# Development Guides and Notes

## Background

### OpenTPOD Architecture

![OpenTPOD Architecture](tpod-arch.png)

### Components

* [docker-compose/.override/prod.yml](../docker-compose.prod.yml): Docker compose file to build, create, and manage all services.
* [nginx](../nginx): Configurations for the Nginx web server. 
  * [opentpod.nginx.conf](../nginx/opentpod.nginx.conf): Setup for the OpenTPOD reverse proxy. It defines the routing information for upstream app_server, and the regex rules for proxying requests to the Django app server. For example, the host name and port for the upstream app server is defined as below. Note that docker-compose creates a dedicated overlay network using container names as host names. Containers on the same overlay network can communicate with each other using their names. You can learn more about docker container networking [here](https://docs.docker.com/compose/networking/).
  ```
  upstream app_server {
    server opentpod:8000 fail_timeout=0;
  }
  ```
  * Compiled React frontend code is copied to ./static by Django's collectstattic
    and mounted to the nginx container by docker-compose. See "volumes" below.
  ```
    opentpod-nginx:
        image: nginx:latest
        container_name: opentpod-nginx
        ports:
            - 0.0.0.0:20000:80
        volumes:
            - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
            - ./nginx/opentpod.nginx.conf:/etc/nginx/opentpod.nginx.conf:ro
            - ./static:/root/openTPOD/static:ro
            - opentpod-data-var:/root/openTPOD/var
        depends_on:
            - opentpod
  ```
* [opentpod](../opentpod): Main Django modules for OpenTPOD. It contains the django-based application server and long-running workers in the diagram above. OpenTPOD Django modules follows Django's directory layout conventions. Read more about Django web framework [here](https://docs.djangoproject.com/en/3.0/). 
  * [Dockerfile](../Dockerfile): Dockerfile for building the container of app server + workers
  * [Django settings](../config/settings): Django settings and configurations. Read more about Django setting files [here](https://docs.djangoproject.com/en/3.0/topics/settings/).
  * [manage.py (Django admin script)](../manage.py): Admin script for OpenTPOD Django app server. Read more about how to use Django's manage.py [here](https://docs.djangoproject.com/en/3.0/ref/django-admin/).
  * [object_detector Django Module](../opentpod/object_detector): Django module serving object detector related Restful APIs, e.g. creating and deleting object detector, creating and deleting training sets.
  * [cvat Django Module](../cvat): External Django module serving video management, annotation Restful APIs and the annotation web app. This is a Git submodule pulling from upstream [CVAT](https://github.com/opencv/cvat) repository.
  * [cvat_ui_adapter Django Module](../opentpod/cvat_ui_adapter): Django module integrating CVAT into OpenTPOD. This modules is an adapater to serve CVAT frontend files to the browser client. This is needed as OpenTPOD's frontend is written in React and served by nginx web server while CVAT's frontend is mosty server-side rendered by the Django template engine.
* Task Queue: Redis is used both as a caching layer for database and a task queue. It is defined in the docker-compose file as the following. Other containers access this Redis instance at "opentpod-redis:6379". 6379 is the default port for Redis.
```
opentpod-redis:
    container_name: opentpod-redis
    image: redis:4.0.5-alpine
    command: --appendonly yes --requirepass "$$OPENTPOD_REDIS_PASSWORD"
    volumes:
        - opentpod-redis-data:/data
```
* Storage: A postgres database instance and a database management web frontend (adminer) are also created by the docker-compose file. They serve as the permanent storage layer for medata and data except videos and images. Video and image data are separately stored in the file system of the opentpod container. Since container's local file system is ephemeral, docker volumes are used to make data persistent. You can read more about managing data in containers [here](https://docs.docker.com/storage/). Volumes "opentpod-db-data" and "opentpod-data-var" respectively persist postgres database and the large video/image data on the file system.

## Authentication

Currently we're using rest_auth and cvat's authentication.

/auth/login/
/auth/logout/
...

## CVAT APIs and workflow

To create a task:
POST /tasks: {name, labels, image_quality, z_order}, notice there is no slash in the end
POST /task/<pk>/data: form data binary
  * calling engine/views.py "task.create" in TaskViewSet-->data
  * calling engine/task.py _create_thread in rq
GET /task/<pk>/status 
DELETE /task/<pk>/status: when server encounters errors

For the dashboard page:
/dashboard/meta
GET /tasks -- represents information for different tasks
/tasks/<task id>/frames/0 -- for a snapshot of the video
