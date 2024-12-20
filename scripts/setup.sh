#!/bin/bash

REPOSITORY_NAME=$(basename $(git rev-parse --show-toplevel)) # Default configuration template depends on the repository name

# 🎨 Color Definitions
COLOR_RESET="\033[0m"
COLOR_GREEN="\033[1;32m"
COLOR_RED="\033[1;31m"
COLOR_YELLOW="\033[1;33m"

# Define the URL of the template repository containing the Git hooks and GitHub Actions files
TEMPLATE_REPO_URL="https://github.com/decodevM/datamaster-dev-standards.git"
TEMPLATE_DIR=".datamaster-dev-standards"

# 📝 Message Definitions
MESSAGE_INIT_REPO="❌  .git directory not found. Please initialize the git repository first using 'git init'."
MESSAGE_CLONE_REPO="Cloning the template repository from"
MESSAGE_CLONE_FAILED="❌  Failed to clone the template repository. Please check the URL and try again."
MESSAGE_CHOOSE_TEMPLATE="Choose a configuration template:"
MESSAGE_COPY_ACTIONS="Copying GitHub Actions templates to the current repository..."
MESSAGE_COPY_HOOKS="Copying Git hooks to .git/hooks..."
MESSAGE_SET_PERMISSIONS="Setting permissions for the Git hooks..."
MESSAGE_SETUP_COMPLETE="✅  Git hooks and GitHub Actions templates have been successfully set up."
MESSAGE_DONE="🎉 Setup complete! You're all set to start enforcing Git message standards in your project."
MESSAGE_INVALID_CHOICE="❌  Invalid choice. Please run the script again and choose a valid option."

# 🌟 Function to print styled messages
print_message() {
  echo -e "$1$2$COLOR_RESET"
}

# 🚨 Check if the current directory is a Git repository
if [ ! -d ".git" ]; then
  print_message "$COLOR_RED" "$MESSAGE_INIT_REPO"
  exit 1
fi


rm -rf "$TEMPLATE_DIR"

# 🔥 Clone the template repository
print_message "$COLOR_YELLOW" "$MESSAGE_CLONE_REPO $TEMPLATE_REPO_URL..."
git clone "$TEMPLATE_REPO_URL" "$TEMPLATE_DIR"

# 🚨 Check if cloning was successful
if [ $? -ne 0 ]; then
  rm -rf "$TEMPLATE_DIR"
  print_message "$COLOR_RED" "$MESSAGE_CLONE_FAILED"
  exit 1
fi

cd "$TEMPLATE_DIR" || exit

if [[ ! -d "$REPOSITORY_NAME" ]]; then
    echo "Error: Repository '$REPOSITORY_NAME' does not exist."
    read -p "Do you want to use the base configuration instead? (yes/no): " USE_BASE
    # Convert input to lowercase for case-insensitive comparison
    USE_BASE=$(echo "$USE_BASE" | tr '[:upper:]' '[:lower:]')
    if [[ "$USE_BASE" =~ ^(yes|y)$ ]]; then
        echo "Using base configuration."
        REPOSITORY_NAME="$BASE_CONFIG"
        if [[ ! -d "$REPOSITORY_NAME" ]]; then
            echo "Error: Base configuration directory does not exist."
            rm -rf "$TEMPLATE_DIR"
            exit 1
        fi
    else
        echo "Operation canceled."
        rm -rf "$TEMPLATE_DIR"
        exit 1
    fi
fi

cd ..

# Add the alias to the local repository's Git configuration
print_message "$COLOR_YELLOW" "Adding alias 'pull-update' to .git/config..."
git config alias.pull-update '!git pull && .git/hooks/post-merge'

# Verify that the alias was added
if git config --get alias.pull-update > /dev/null; then
  print_message "$COLOR_GREEN" "Alias 'pull-update' successfully added to .git/config!"
else
  print_message "$COLOR_RED" "Failed to add alias 'pull-update'."
fi

# 📂 Copy the selected configuration
cd "$TEMPLATE_DIR/$REPOSITORY_NAME" || exit

# 📑 Copy the GitHub Actions files
print_message "$COLOR_YELLOW" "$MESSAGE_COPY_ACTIONS"
rm -rf ../../.github  # Remove existing .github directory
mkdir ../../.github   # Recreate the .github directory
cp -r .github/* ../../.github/


# 🔑 Copy the Git hooks
print_message "$COLOR_YELLOW" "Overwriting existing commit-msg hook..."
cp hooks/* ../../.git/hooks/
chmod +x ../../.git/hooks/*


# 🔄 Return to the main repository folder
cd ../..

# ✅ Confirm the setup
print_message "$COLOR_GREEN" "$MESSAGE_SETUP_COMPLETE"

# 🧹 Optionally, remove the template repository after setup
rm -rf "$TEMPLATE_DIR"

# 🎉 Done
print_message "$COLOR_GREEN" "$MESSAGE_DONE"