#!/bin/bash

docker image tag d_host:latest d_host_old:latest;
docker build -t d_host --file ./Dockerfile.d_host . &&
docker rmi d_host_old

docker image tag d_router:latest d_router_old:latest;
docker build -t d_router --file ./Dockerfile.d_router . &&
docker rmi d_router_old
