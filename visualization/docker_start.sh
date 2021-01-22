#!/usr/bin/env bash
echo "Starting internal launch script...."
sleep 3
until cd /var/www/apache-flask/app
do
    echo "Waiting for mount"
    sleep 1
done
echo `date` > /var/www/apache-flask/app/start.timestamp
apachectl -D FOREGROUND
