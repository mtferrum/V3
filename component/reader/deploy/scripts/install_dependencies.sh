#!/usr/bin/env bash
echo $(
    #Python venv and dependencies
    #python3 -m venv /opt/projects/venv;
    #source /opt/projects/venv/bin/activate;
    cd /opt/projects/mvid/component/reader/deploy;
    pip3 install -r requirements.txt;
    #deactivate;
)
