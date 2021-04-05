#!/usr/bin/env bash
echo $(
    #Configure, run and enable service

    if [[ ! -f /etc/spyspace/mvid_conf.yaml ]]; then
        cp /opt/projects/mvid/scope/data/mvid_conf.yaml /etc/spyspace/;
    fi
    bash /opt/projects/mvid/component/alerter/deploy/scripts/create_environment_file.sh;
    #Create and enable alerter service
    sudo cp /opt/projects/mvid/component/alerter/deploy/alerter.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start alerter;
    sudo systemctl enable alerter;
    #Create and enable subscriber service
    sudo cp /opt/projects/mvid/component/alerter/deploy/subscriber_black.service /etc/systemd/system/;
    sudo cp /opt/projects/mvid/component/alerter/deploy/subscriber_white.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start subscriber_black;
    sudo systemctl start subscriber_white;
    sudo systemctl enable subscriber_black;
    sudo systemctl enable subscriber_white;
)
