#!/bin/bash

set -x
export CHANNEL="dev"
export ORG="fmtr"
export PACKAGE="tools"
export PORT="2200"
export BASE="pytorch"
export HOST="compute"
export COMPUTE="gpu"
export EXTRAS="pdf,logging,debug,ai.client,sets"

export VERSION=$(<"${ORG}/${PACKAGE}/version")
export DOCKER_HOST=ssh://ed@${HOST}.lan

docker compose build
docker compose --file compose.yml --file compose.${COMPUTE}.yml --project-name "${ORG}"-"${PACKAGE}" up --detach --force-recreate
