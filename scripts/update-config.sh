#!/bin/bash

# 🎨 Color Definitions
COLOR_RESET="\033[0m"
COLOR_GREEN="\033[1;32m"
COLOR_RED="\033[1;31m"
COLOR_YELLOW="\033[1;33m"

# Template repository URL
TEMPLATE_REPO_URL="https://github.com/decodevM/datamaster-dev-standards.git"
TEMPLATE_DIR=".temp-templates"

cd ../..  # Ensure we're in the project root

# Get repository name
REPOSITORY_NAME=$(basename $(git rev-parse --show-toplevel)) # Get the repository name
cd .git
# echo "Repository Name: $REPOSITORY_NAME"

# 🌟 Function to print styled messages
print_message() {
  echo -e "$1$2$COLOR_RESET"
}

# 🔥 Clone or update the template repository
if [ -d "$TEMPLATE_DIR" ]; then
  # print_message "$COLOR_YELLOW" "Updating template repository..."
  cd "$TEMPLATE_DIR" && git pull origin main && cd ..
else
  # print_message "$COLOR_YELLOW" "Cloning the template repository..."
  git clone "$TEMPLATE_REPO_URL" "$TEMPLATE_DIR"
fi



# 🚨 Check if cloning or updating was successful
if [ $? -ne 0 ]; then
  print_message "$COLOR_RED" "Failed to fetch the template repository. Please check the URL or connection."
  exit 1
fi



# 📂 Check if the repository-specific configuration exists
CONFIG_DIR="$TEMPLATE_DIR/$REPOSITORY_NAME"
if [ ! -d "$CONFIG_DIR" ]; then
  print_message "$COLOR_RED" "No configuration found for repository: $REPOSITORY_NAME. Please ensure it exists in the template repository."
  exit 1
fi

# 📑 Update GitHub Actions
# print_message "$COLOR_YELLOW" "Updating GitHub Actions..."
rm -rf ../.github
mkdir ../.github
cp -r "$CONFIG_DIR/.github/"* ../.github/

# 🔑 Update commit-msg hook
# print_message "$COLOR_YELLOW" "Updating commit-msg hook..."
cp "$CONFIG_DIR/hooks/"* hooks/
chmod +x hooks/*

# 🧹 Optionally clean up temporary files
# print_message "$COLOR_GREEN" "Update completed successfully."