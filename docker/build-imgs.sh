#!/bin/bash

set -e

if [ "${#}" -eq 2 ]; then
  image_name="${1}"
  path_dockerfile="${2}"
  version=$(echo "${2}" | sed -E 's/\/.+//')
  variant=$(echo "${2}" | sed -E 's/[0-9]+\.[0-9]+\///')
  variant="${variant%Dockerfile}"
  variant="${variant%%/}"
  tag="${version}-${variant}"
else
  echo "usage : $0 IMAGE_NAME PATH_TO_DOCKERFILE"
  echo ""
  echo 'Pass opts to `docker build` in base, if set `$XROSFS_DOCKER_BUILD_BASE_OPTS`.' 
  echo 'Pass opts to `docker build` in dev, if set `$XROSFS_DOCKER_BUILD_DEV_OPTS`.' 
  exit 1
fi

docker build ${XROSFS_DOCKER_BUILD_BASE_OPTS} -t "${image_name}":"${tag}" "${path_dockerfile%%/}"/base
docker build ${XROSFS_DOCKER_BUILD_DEV_OPTS} --build-arg BASE_IMAGE="${image_name}":"${tag}" -t "${image_name}-dev":"${tag}" "${path_dockerfile%%/}"/dev
