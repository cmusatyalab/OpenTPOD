#!/bin/bash -ex

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# collect CVAT static files
python manage.py collectstatic --noinput
# build TPOD react
cd frontend
npm install
npm run-script build

# go back to root directory
cd ${CUR_DIR}
mkdir -p www
rm -rf www/*
mv frontend/build/* www/
ln -rs static www/django-static

printf "Frontend build successful!"
printf "nginx should serve DIR: $(readlink -f www)"
