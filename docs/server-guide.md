---
description: Explains how to setup OpenTPOD server.
---

# Installation

```
$ conda env create -f requirements/environment-dev.yml
$ ln -s third_party/cvat/cvat cvat
$ # for developemnt
$ source .envrc
$ docker-compose up
$ supervisord -n -c supervisord/dev.conf
$ # for deployment
$ source .envrc.prod
$ docker-compose -f docker-compose.prod.yml up

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

An example client code to query TF serving container can be found under [opentpod/object\_detector/provider/tfod/infer.py](https://github.com/junjuew/OpenTPOD/blob/master/opentpod/object_detector/provider/tfod/infer.py).

