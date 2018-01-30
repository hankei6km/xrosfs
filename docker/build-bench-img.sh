#!/bin/bash

set -e

setup_basic_script="setup-bench-basic-data.sh"
setup_relpath_script="setup-bench-relpath-data.sh"
setup_useruri_script="setup-bench-useruri-data.sh"

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
  echo 'Pass opts to `docker build` in bench, if set `$XROSFS_DOCKER_BUILD_BENCH_OPTS`.' 
  exit 1
fi

cp "${version}/${setup_basic_script}" "${path_dockerfile%%/}"/bench/
cp "${version}/${setup_relpath_script}" "${path_dockerfile%%/}"/bench/
cp "${version}/${setup_useruri_script}" "${path_dockerfile%%/}"/bench/
docker build ${XROSFS_DOCKER_BUILD_BENCH_OPTS} -t "${image_name}":"${tag}" "${path_dockerfile%%/}"/bench
