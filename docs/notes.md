# Development Notes

## Authentication

Using rest_auth and cvat's authentication

/auth/login/
/auth/logout/
...

## Test Account

tpod:admin-test

## CVAT workflow

To create a task:
POST /tasks: {name, labels, image_quality, z_order}
POST /task/<pk>/data: form data binary
GET /task/<pk>/status 
DELETE /task/<pk>/status: when server encounters errors

Client-side DOM id: DashboardCreateContent

For the dashboard page:
/dashboard/meta
GET /tasks -- represents information for different tasks
/tasks/<task id>/frames/0 -- for a snapshot of the video

## TODO:

1. finish rest api first. add classifier, job APIs
2. write tests for these rest apis, combining both CVAT and opentpod.
  1. see CVAT's tests for example