#!/bin/bash -ex

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# collect CVAT static files
python manage.py collectstatic
# build TPOD react
cd frontend
npm run-script build

# go back to root directory
cd ${CUR_DIR}
rm -rf www
mkdir -p www
mv frontend/build/* www/
ln -rs static www/django-static

printf "Frontend build successful!"
printf "nginx should serve DIR: $(readlink -f www)"
