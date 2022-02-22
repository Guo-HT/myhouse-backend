#!/bin/bash

datetime=`date '+%Y-%m-%d %H:%M:%S'`
date=${datetime:0:10}
time=${datetime:11:8}
datetime=$date'~'$time

logs_root='/home/pi/Code/Django_proj/MyHouse_Backend/logs/'
log_file_name=$logs_root$date".log"


touch $log_file_name
cat /home/pi/Code/Django_proj/MyHouse_Backend/gunicorn_access.log > $log_file_name
#awk 'NR>2{print}' /home/pi/Code/Django_proj/MyHouse_Backend/gunicorn_access.log
echo '************' > /home/pi/Code/Django_proj/MyHouse_Backend/gunicorn_access.log

