#!/bin/sh

NOW=$(date -Iseconds)

#docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
#    exec -T opentpod tar -czf - -C /root/openTPOD/var data > ${NOW}_data.tgz
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
    exec -T opentpod tar -czf - -C /root/openTPOD/var . > ${NOW}_data.tgz

docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
    exec opentpod-db pg_dumpall -c -U root | gzip -9 > ${NOW}_pgdump.gz

# restore
# cat data.tgz | docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
#   exec -T opentpod tar -xzf - -C /root/openTPOD/var
#     
# zcat pgdump.gz | docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
#   exec opentpod-db psql -U root
