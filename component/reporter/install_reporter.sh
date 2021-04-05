#!/bin/bash
SCRIPT_DIR=$(dirname "$0")

echo 'INSTALL PACK'

#apt install nginx npm uwsgi uwsgi-plugin-python3 mosquitto openssh-server curl -y
apt install nginx uwsgi uwsgi-plugin-python3 mosquitto openssh-server curl -y

chmod  -R  777 /var/log/spyspace
echo 'NGIXN CONF'
rm /etc/nginx/sites-enabled/default
cp deploy/nginx.conf /etc/nginx/sites-enabled/nginx.conf

echo 'UWSGI CONF'
cp deploy/reporter.ini /etc/uwsgi/apps-enabled/whitelist.ini

echo 'RESTARTING'
systemctl restart nginx
systemctl restart uwsgi