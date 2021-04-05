#!/usr/bin/env bash
echo $(
    #Configure, run and enable api with UWSGI as service

    if [[ ! -f /etc/spyspace/mvid_conf.yaml ]]; then
        cp /opt/projects/mvid/scope/data/mvid_conf.yaml /etc/spyspace/;
    fi
    cp /opt/projects/mvid/component/http_api/deploy/api_mvideo_wsgi.ini /etc/spyspace/
    bash /opt/projects/mvid/component/http_api/deploy/scripts/create_environment_file.sh;
    sudo cp /opt/projects/mvid/component/http_api/deploy/api_mvideo.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start api_mvideo;
    sudo systemctl enable api_mvideo;
    #Create and enable listener service
    sudo cp /opt/projects/mvid/component/http_api/deploy/listener_mvideo.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start listener_mvideo;
    sudo systemctl enable listener_mvideo;
)
