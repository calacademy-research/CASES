#!/bin/bash
cd "$(dirname "$0")"
parentdir="$(dirname `pwd`)"
echo $parentdir
docker run \
-v `pwd`:/var/www/apache-flask/app \
-v $parentdir/employment_by_sector_by_month:/var/www/apache-flask/employment_by_sector_by_month \
-v $parentdir/age_fracs:/var/www/apache-flask/age_fracs \
-v $parentdir/r:/var/www/apache-flask/r \
-v $parentdir/employment_by_sector_Feb2020://var/www/apache-flask/employment_by_sector_Feb2020 \
-d -p 80:80 --name CASES  -i -t apache-flask /bin/bash -restart
