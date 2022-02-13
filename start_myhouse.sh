
nohup gunicorn -c gunicorn.conf.py MyHouse.wsgi:application &
# nohup uwsgi --ini uwsgi_.ini > uwsgi.log &

# nohup python ./mqtt_sub.py > mqtt.log &