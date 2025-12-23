#!/usr/bin/env bash
set -o errexit

echo "Installing dependencies with uv..."
uv sync --frozen --no-install-project --no-dev

echo "Collecting static files..."
uv run python src/manage.py collectstatic --no-input

echo "Running database migrations..."
uv run python src/manage.py migrate

echo "Build completed successfully!"