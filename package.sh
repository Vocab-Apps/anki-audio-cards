#!/bin/bash

set -eoux pipefail

if [ -z "${1:-}" ]; then
  echo "Please pass major, minor or patch"
  exit 1
fi

BUMP_TYPE=$1
if [ "$BUMP_TYPE" != "major" ] && [ "$BUMP_TYPE" != "minor" ] && [ "$BUMP_TYPE" != "patch" ]; then
  echo "Please pass major, minor or patch"
  exit 1
fi

CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
  echo "Error: must be on branch 'main' to release (currently on '$CURRENT_BRANCH')"
  exit 1
fi

NEW_VERSION=$(bump2version --list "${BUMP_TYPE}" | grep new_version | sed -r s,"^.*=",,)

git push
git push --tags

VERSION_NUMBER=${NEW_VERSION}

rm -f meta.json
rm -rf __pycache__
rm -rvf htmlcov/

mkdir -p "${HOME}/anki-addons-releases"
ADDON_FILENAME=${HOME}/anki-addons-releases/anki-audio-cards-${VERSION_NUMBER}.ankiaddon
zip -r "${ADDON_FILENAME}" manifest.json external/ config.json __init__.py audiocards_addon/ --exclude "*__pycache__*"

rclone sync ~/anki-addons-releases/ dropbox:Anki/anki-addons-releases/
