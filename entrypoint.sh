#! /bin/bash

python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py collectstatic --noinput

python manage.py loaddata fixturas.json

exec supervisord -c supervisord_prod.conf