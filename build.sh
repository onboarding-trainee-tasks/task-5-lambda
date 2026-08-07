#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DIST_DIR="${PROJECT_DIR}/dist"
LAYER_DIR="${DIST_DIR}/layer"
FUNCTION_DIR="${DIST_DIR}/function"

echo "Cleaning old build..."

rm -rf "${DIST_DIR}"

mkdir -p "${LAYER_DIR}/python"
mkdir -p "${FUNCTION_DIR}"


echo "Installing requests..."

python3 -m pip install \
  --requirement "${PROJECT_DIR}/requirements.txt" \
  --target "${LAYER_DIR}/python"


echo "Preparing Lambda function..."

cp \
  "${PROJECT_DIR}/lambda_function.py" \
  "${FUNCTION_DIR}/lambda_function.py"


echo "Creating Lambda Layer ZIP..."

cd "${LAYER_DIR}"

zip -qr \
  "${DIST_DIR}/requests-layer.zip" \
  python


echo "Creating Lambda function ZIP..."

cd "${FUNCTION_DIR}"

zip -q \
  "${DIST_DIR}/lambda-function.zip" \
  lambda_function.py


echo "Removing temporary directories..."

rm -rf "${LAYER_DIR}"
rm -rf "${FUNCTION_DIR}"


echo
echo "Build finished."
echo "Lambda: ${DIST_DIR}/lambda-function.zip"
echo "Layer:  ${DIST_DIR}/requests-layer.zip"