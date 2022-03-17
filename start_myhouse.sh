celery_log_path="/root/project/var/log/celery.log"

nohup gunicorn -c gunicorn.conf.py MyHouse.wsgi:application &

nohup celery -A celery_tasks.email_task worker -l info > $celery_log_path &

# nohup uwsgi --ini uwsgi_.ini > uwsgi.log &

# nohup python ./mqtt_sub.py > mqtt.log &
