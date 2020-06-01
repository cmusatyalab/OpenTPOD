# Development Guides and Notes

## Background

### OpenTPOD Architecture

![OpenTPOD Architecture](tpod-arch.png)

### Components

* [docker-compose.debug/prod.yml](../docker-compose.prod.yml): Docker compose file to build, create, and manage all services.
* [opentpod](../opentpod): Main Django module for OpenTPOD. It contains the django-based application server and long-running workers in the diagram above.
  * [Dockerfile](../Dockerfile): Dockerfile for building the container of app server + workers
  * [supervisord](../supervisord): Supervisord configuration files that launches the app server + workers inside the opentpod container. Using supervisord to launch all app and worker processes are set to be the default command in the Dockerfile.
    * [production.conf](../supervisord/production.conf): The production configurations launches 4 processes: app server, rqworker_low, rqworker_default, rqworker_tensorboard. rqworker_* are long-running workers grouped by their priorities. You can change how many rqworkers are launched with the "numprocs" configuration.
  * [object_detector Django Module](../opentpod/object_detector): Django module serving object detector related Restful APIs, e.g. creating and deleting object detector, creating and deleting training sets.
  * [cvat Django Module](../cvat): External Django module serving video management, annotation Restful APIs and the annotation web app. This is a Git submodule pulling from upstream [CVAT](https://github.com/opencv/cvat) repository.
  * [cvat_ui_adapter Django Module](../opentpod/cvat_ui_adapater): Django module integration CVAT into OpenTPOD. This modules is an adapater to serve CVAT frontend files to the browser client. This is needed as OpenTPOD's frontend is written in React and served by nginx web server while CVAT's frontend is mosty server-side rendered by the Django template engine.
* [nginx](../nginx): Configurations for the Nginx web server. 
  * [opentpod.nginx.conf](../nginx/opentpod.nginx.conf): Setup for OpenTPOD reverse proxy. It defines the routing information for upstream app_server, and the requests that need to be proxied to the Django app server.
  * Compiled React frontend code is mounted to the nginx container by docker-compose. See "volumes".
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
            - ./www:/root/openTPOD/www:ro
            - opentpod-data-var:/root/openTPOD/var
        depends_on:
            - opentpod
  ```

## Authentication

Using rest_auth and cvat's authentication

/auth/login/
/auth/logout/
...

## CVAT workflow

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
