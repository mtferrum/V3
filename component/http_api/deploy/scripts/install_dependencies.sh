#!/usr/bin/env bash
echo $(
    #System dependencies
    (sudo apt install -y nginx npm python3-dev python3-venv;)
    #Python venv and dependencies
    python3 -m venv /opt/projects/venv;
    source /opt/projects/venv/bin/activate;
    cd /opt/projects/mvid/component/http_api/deploy;
    pip install -r requirements.txt;
    deactivate;
    #NPM dependencies
    cd /opt/projects/mvid/frontend;
    npm install;
)
