#!/usr/bin/env sh
# Builds static/dist inside a Node container so no npm or yarn runs on the host.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
docker run --rm -v "$ROOT":/app -w /app/build node:22-slim sh -c "yarn install && yarn build"
