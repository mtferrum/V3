#!/usr/bin/env bash
echo $(
    cd /opt/projects/mvid/frontend;
    npm run build;
    sudo rm /etc/nginx/sites-enabled/default;
    sudo cp /opt/projects/mvid/component/http_api/deploy/mvideo_nginx.conf /etc/nginx/sites-enabled;
    sudo chown tech:tech /opt/projects/mvid/component/http_api/deploy/mvideo_nginx.conf;
    sudo systemctl restart nginx;
)