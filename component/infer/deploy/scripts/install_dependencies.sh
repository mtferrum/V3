#!/usr/bin/env bash
echo $(
    #System dependencies
    #Python venv and dependencies
    #python3 -m venv /opt/projects/venv;
    source /opt/projects/venv/bin/activate;
    cd /opt/projects/mvid/component/infer/deploy;
    pip install -r requirements.txt;
    deactivate;
)
