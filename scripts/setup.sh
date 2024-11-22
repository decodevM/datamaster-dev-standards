#!/bin/bash

# 🎨 Color Definitions
COLOR_RESET="\033[0m"
COLOR_GREEN="\033[1;32m"
COLOR_RED="\033[1;31m"
COLOR_YELLOW="\033[1;33m"

# Define the URL of the template repository containing the Git hooks and GitHub Actions files
#TEMPLATE_REPO_URL="https://github.com/decodevM/git-message-standards.git"
TEMPLATE_REPO_URL="https://github.com/decodevM/datamaster-dev-standards.git"
TEMPLATE_DIR="datamaster-dev-standards"

# 📝 Message Definitions
MESSAGE_INIT_REPO="❌  .git directory not found. Please initialize the git repository first using 'git init'."
MESSAGE_CLONE_REPO="Cloning the template repository from"
MESSAGE_CLONE_FAILED="❌  Failed to clone the template repository. Please check the URL and try again."
MESSAGE_COPY_ACTIONS="Copying GitHub Actions templates to the current repository..."
MESSAGE_COPY_HOOKS="Copying Git hooks to .git/hooks..."
MESSAGE_SET_PERMISSIONS="Setting permissions for the Git hooks..."
MESSAGE_SETUP_COMPLETE="✅  Git hooks and GitHub Actions templates have been successfully set up."
MESSAGE_DONE="🎉 Setup complete! You're all set to start enforcing Git message standards in your project."

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

# 🔥 Cloning the template repository
print_message "$COLOR_YELLOW" "$MESSAGE_CLONE_REPO $TEMPLATE_REPO_URL..."
git clone "$TEMPLATE_REPO_URL" "$TEMPLATE_DIR"

# 🚨 Check if cloning was successful
if [ $? -ne 0 ]; then
  print_message "$COLOR_RED" "$MESSAGE_CLONE_FAILED"
  exit 1
fi

# 📂 Move into the template repository directory
cd "$TEMPLATE_DIR" || exit

# 📑 Copy the GitHub Actions files to the main project directory, but check if they exist first
if [ -d "../.github" ]; then
  read -p "⚠️ .github directory exists. Do you want to overwrite it? (y/n): " overwrite_actions
  if [[ "$overwrite_actions" == "y" || "$overwrite_actions" == "Y" ]]; then
    print_message "$COLOR_YELLOW" "$MESSAGE_COPY_ACTIONS"
    rm -rf ../.github  # Remove the existing .github directory
    mkdir ../.github   # Recreate the .github directory to avoid the "not a directory" error
    cp -r .github/* ../.github/  # Copy the new GitHub Actions folder from the template
  else
    print_message "$COLOR_GREEN" "💡 Skipping .github directory overwrite."
  fi
else
  print_message "$COLOR_YELLOW" "$MESSAGE_COPY_ACTIONS"
  mkdir ../.github   # Create the .github directory if it doesn't exist
  cp -r .github/* ../.github/  # Copy GitHub Actions folder if it doesn't exist
fi

# 🔑 Copy the contents of the hooks directory to the existing .git/hooks
if [ -d "../.git/hooks" ]; then
  read -p "⚠️ .git/hooks directory exists. Do you want to overwrite it? (y/n): " overwrite_hooks
  if [[ "$overwrite_hooks" == "y" || "$overwrite_hooks" == "Y" ]]; then
    print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
    cp -r hooks/* ../.git/hooks/  # Copy only the contents of the hooks directory
    print_message "$COLOR_YELLOW" "$MESSAGE_SET_PERMISSIONS"
    chmod -R +x ../.git/hooks/*  # Ensure all scripts in the hooks directory are executable
  else
    print_message "$COLOR_GREEN" "💡 Skipping .git/hooks directory overwrite."
  fi
else
  print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
  cp -r hooks/* ../.git/hooks/  # Copy only the contents of the hooks directory
  print_message "$COLOR_YELLOW" "$MESSAGE_SET_PERMISSIONS"
  chmod -R +x ../.git/hooks/*  # Ensure all scripts in the hooks directory are executable
fi

# 🛠️ Set the appropriate permissions for the Git hooks (if needed)
# This was already handled in the above logic where hooks are copied

# 🔄 Go back to the main repository folder
cd ..

# ✅ Confirm the setup
print_message "$COLOR_GREEN" "$MESSAGE_SETUP_COMPLETE"

# 🧹 Optionally, you can remove the template repository directory after setup
# Uncomment the line below if you want to remove the template repo after setup
 rm -rf "$TEMPLATE_DIR"

# 🎉 Done
print_message "$COLOR_GREEN" "$MESSAGE_DONE"