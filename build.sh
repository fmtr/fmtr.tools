#!/bin/bash

set -x
export CHANNEL="dev"
export ORG="fmtr"
export PACKAGE="tools"
export PORT="2200"
export BASE="python"
export VERSION=$(<"${ORG}/${PACKAGE}/version")

if [ "$CHANNEL" = "dev" ]; then
    export DOCKER_HOST=ssh://ed@ws.lan
else
    export DOCKER_HOST=ssh://ed@compute.lan
fi

docker compose build
docker compose --project-name "${ORG}"-"${PACKAGE}" up --detach
