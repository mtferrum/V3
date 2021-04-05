#!/usr/bin/env bash
echo $(
    #Configure, run and enable service

    if [[ ! -f /etc/spyspace/mvid_conf.yaml ]]; then
        cp /opt/projects/mvid/scope/data/mvid_conf.yaml /etc/spyspace/;
    fi
    bash /opt/projects/mvid/utill/deploy/scripts/create_environment_file.sh;
    #Create and enable redis_monitor service
    sudo cp /opt/projects/mvid/utill/deploy/redis_monitor.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start redis_monitor;
    sudo systemctl enable redis_monitor;
)
