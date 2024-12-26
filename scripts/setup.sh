#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Log function for better readability
log() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}

log "Installing Poetry..."

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the PATH (for the current session)
export PATH="$HOME/.local/bin:$PATH"

# Disable virtualenv creation (use system Python environment)
poetry config virtualenvs.create true

log "Poetry installation complete."

# Verify installation
poetry --version

log "Installing project dependencies with Poetry..."

# Install project dependencies
poetry install

log "Installing playwright..."

poetry add playwright pytest-playwright

poetry run playwright install

poetry run playwright install-deps

poetry add pytest-bdd

log "Project setup complete!"