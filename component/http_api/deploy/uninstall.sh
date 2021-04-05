#!/usr/bin/env bash
echo $(
    #Services
    sudo systemctl disable listener_mvideo;
    sudo systemctl disable api_mvideo;
    sudo systemctl stop listener_mvideo;
    sudo systemctl stop api_mvideo;
    sudo rm /etc/systemd/system/api_mvideo.service;
    sudo rm /etc/systemd/system/listener_mvideo.service;
    sudo systemctl daemon-reload;
    #Configuration
    rm /etc/spyspace/api_mvideo_wsgi.ini;
    rm /etc/nginx/sites-enabled/mvideo_nginx.conf;
    sudo systemctl restart nginx;
)