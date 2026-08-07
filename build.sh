#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DIST_DIR="${PROJECT_DIR}/dist"
LAYER_BUILD_DIR="${DIST_DIR}/layer"
FUNCTION_BUILD_DIR="${DIST_DIR}/function"

LAYER_ZIP="${DIST_DIR}/requests-layer.zip"
FUNCTION_ZIP="${DIST_DIR}/lambda-function.zip"

echo "Cleaning old build files..."

rm -rf "${DIST_DIR}"

mkdir -p "${LAYER_BUILD_DIR}/python"
mkdir -p "${FUNCTION_BUILD_DIR}"

echo "Installing requests library..."

python3 -m pip install \
  --no-cache-dir \
  --requirement "${PROJECT_DIR}/requirements.txt" \
  --target "${LAYER_BUILD_DIR}/python"

echo "Copying Lambda function..."

cp \
  "${PROJECT_DIR}/lambda_function.py" \
  "${FUNCTION_BUILD_DIR}/lambda_function.py"

echo "Creating requests Layer ZIP..."

cd "${LAYER_BUILD_DIR}"

zip -qr \
  "${LAYER_ZIP}" \
  python

echo "Creating Lambda function ZIP..."

cd "${FUNCTION_BUILD_DIR}"

zip -q \
  "${FUNCTION_ZIP}" \
  lambda_function.py

echo "Removing temporary build directories..."

rm -rf "${LAYER_BUILD_DIR}"
rm -rf "${FUNCTION_BUILD_DIR}"

echo
echo "Build completed."
echo "Lambda function: ${FUNCTION_ZIP}"
echo "Lambda Layer:    ${LAYER_ZIP}"