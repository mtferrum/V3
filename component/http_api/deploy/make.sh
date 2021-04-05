#!/usr/bin/env bash
echo $(
    echo "INSTALLING DEPENDENCIES...\n";
    bash  /opt/projects/mvid/component/http_api/deploy/scripts/install_dependencies.sh $1;
    echo "PREPARING DIRECTORIES...\n";
    sudo bash  /opt/projects/mvid/component/http_api/deploy/scripts/create_dirs.sh;
    echo "BUILDING OPENVINO ENVIRONMENT FILE\n";
    bash  /opt/projects/mvid/component/http_api/deploy/scripts/create_environment_file.sh;
    echo "DEPLOYING BACKEND SERVICES...\n";
    bash  /opt/projects/mvid/component/http_api/deploy/scripts/deploy_api.sh;
    echo "DEPLOYING FRONTEND...\n";
    bash  /opt/projects/mvid/component/http_api/deploy/scripts/deploy_frontend.sh;
    echo "DONE\n";
)
