#!/usr/bin/env bash
echo $(
    sudo mkdir /etc/spyspace;
    sudo chown -R tech:tech /etc/spyspace;
    sudo mkdir /var/spyspace;
    mkdir /var/spyspace/photos;
    mkdir /var/spyspace/videos;
    sudo chown -R tech:tech /var/spyspace;
    sudo mkdir /var/log/spyspace;
    sudo chown -R tech:tech /var/log/spyspace;
)