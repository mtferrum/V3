#!/usr/bin/env bash
echo $(
    #Configure, run and enable service

    if [[ ! -f /etc/spyspace/mvid_conf.yaml ]]; then
        cp /opt/projects/mvid/scope/data/mvid_conf.yaml /etc/spyspace/;
    fi
    bash /opt/projects/mvid/component/reader/deploy/scripts/create_environment_file.sh;
    #Create and enable reader service
    sudo cp /opt/projects/mvid/component/reader/deploy/reader.service /etc/systemd/system/;
    sudo systemctl daemon-reload;
    sudo systemctl start reader;
    sudo systemctl enable reader;
)
