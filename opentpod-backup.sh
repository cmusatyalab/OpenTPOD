#!/bin/sh

set -e

PREFIX=${1:-$(date -Iseconds)}

docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
    exec -T opentpod tar -cf - -C /root/openTPOD/var . > "${PREFIX}_data.tar.tmp"

docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
    exec opentpod-db pg_dumpall -c -U root | gzip -9 --rsyncable > "${PREFIX}_pgdump.gz.tmp"

mv "${PREFIX}_data.tar.tmp" "${PREFIX}_data.tar"
mv "${PREFIX}_pgdump.gz.tmp" "${PREFIX}_pgdump.gz"

##
## RESTORE
##
## restore saved user-data, frames, trained models, and other media.
## using docker because I was having issues with docker-compose exec and stdin
# cat data.tar | docker exec -i opentpod tar -C /root/openTPOD/var -xf -
#
## stop all containers except for the database so we can repopulate tables
# docker-compose -f docker-compose.yml -f docker-compose.prod.yml stop
# docker-compose -f docker-compose.yml -f docker-compose.prod.yml start opentpod-db
#
## restore database
# zcat pgdump.gz | docker exec -i opentpod-db psql -U root postgres
#
## bring everything back online
# (make sure your local .env has the original db password configured)
# docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
