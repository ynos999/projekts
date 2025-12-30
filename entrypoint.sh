#! /bin/bash

python manage.py makemigrations --no-input

python manage.py migrate --no-input

python manage.py loaddata fixturas.json

# exec supervisord -c supervisord_prod.conf