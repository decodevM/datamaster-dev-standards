#!/bin/bash

# 🎨 Color Definitions
COLOR_RESET="\033[0m"
COLOR_GREEN="\033[1;32m"
COLOR_RED="\033[1;31m"
COLOR_YELLOW="\033[1;33m"

# Define the URL of the template repository containing the Git hooks and GitHub Actions files
TEMPLATE_REPO_URL="https://github.com/decodevM/datamaster-dev-standards.git"
TEMPLATE_DIR="datamaster-dev-standards"

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
MESSAGE_INVALID_CHOICE="❌ Invalid choice. Please run the script again and choose a valid option."

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

# 🌀 Ask the user to choose a configuration template
print_message "$COLOR_YELLOW" "$MESSAGE_CHOOSE_TEMPLATE"
echo "1) box"
echo "2) task"
read -p "Enter the number of your choice: " template_choice

case "$template_choice" in
  1)
    CONFIG_DIR="box"
    ;;
  2)
    CONFIG_DIR="task"
    ;;
  *)
    print_message "$COLOR_RED" "$MESSAGE_INVALID_CHOICE"
    rm -rf "$TEMPLATE_DIR"
    exit 1
    ;;
esac

# 📂 Copy the selected configuration
cd "$TEMPLATE_DIR/$CONFIG_DIR" || exit

# 📑 Copy the GitHub Actions files
if [ -d "../../.github" ]; then
  read -p "⚠️ .github directory exists. Do you want to overwrite it? (y/n): " overwrite_actions
  if [[ "$overwrite_actions" == "y" || "$overwrite_actions" == "Y" ]]; then
    print_message "$COLOR_YELLOW" "$MESSAGE_COPY_ACTIONS"
    rm -rf ../../.github  # Remove existing .github directory
    mkdir ../../.github   # Recreate the .github directory
    cp -r .github/* ../../.github/
  else
    print_message "$COLOR_GREEN" "💡 Skipping .github directory overwrite."
  fi
else
  print_message "$COLOR_YELLOW" "$MESSAGE_COPY_ACTIONS"
  mkdir ../../.github
  cp -r .github/* ../../.github/
fi


# # 🔑 Copy the Git hooks
# if [ -d "../../.git/hooks" ]; then
#   read -p "⚠️ .git/hooks directory exists. Do you want to overwrite it? (y/n): " overwrite_hooks
#   if [[ "$overwrite_hooks" == "y" || "$overwrite_hooks" == "Y" ]]; then
#     print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
#     cp -r hooks/* ../../.git/hooks/
#     print_message "$COLOR_YELLOW" "$MESSAGE_SET_PERMISSIONS"
#     chmod -R +x ../../.git/hooks/*
#   else
#     print_message "$COLOR_GREEN" "💡 Skipping .git/hooks directory overwrite."
#   fi
# else
#   print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
#   cp -r hooks/* ../../.git/hooks/
#   print_message "$COLOR_YELLOW" "$MESSAGE_SET_PERMISSIONS"
#   chmod -R +x ../../.git/hooks/*
# fi




# 🔑 Copy the Git hooks
if [ -d "../../.git/hooks" ]; then
  # Check if the `commit-msg` hook exists
  if [ -f "../../.git/hooks/commit-msg" ]; then
    read -p "⚠️ commit-msg hook already exists. Do you want to overwrite it? (y/n): " overwrite_commit_msg
    if [[ "$overwrite_commit_msg" == "y" || "$overwrite_commit_msg" == "Y" ]]; then
      print_message "$COLOR_YELLOW" "Overwriting existing commit-msg hook..."
      cp hooks/commit-msg ../../.git/hooks/commit-msg
      chmod +x ../../.git/hooks/commit-msg
    else
      print_message "$COLOR_GREEN" "💡 Skipping commit-msg hook overwrite."
    fi
  else
    # If commit-msg doesn't exist, copy it
    print_message "$COLOR_YELLOW" "Adding new commit-msg hook..."
    cp hooks/commit-msg ../../.git/hooks/commit-msg
    chmod +x ../../.git/hooks/commit-msg
  fi

  # # Copy other hooks
  # read -p "⚠️ .git/hooks directory exists. Do you want to overwrite other hooks? (y/n): " overwrite_hooks
  # if [[ "$overwrite_hooks" == "y" || "$overwrite_hooks" == "Y" ]]; then
  #   print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
  #   cp -r hooks/* ../../.git/hooks/
  #   chmod -R +x ../../.git/hooks/*
  # else
  #   print_message "$COLOR_GREEN" "💡 Skipping other hooks overwrite."
  # fi
else
  # If .git/hooks directory doesn't exist, copy everything
  print_message "$COLOR_YELLOW" "$MESSAGE_COPY_HOOKS"
  cp -r hooks/* ../../.git/hooks/
  chmod -R +x ../../.git/hooks/*
fi

# 🔄 Return to the main repository folder
cd ../..

# ✅ Confirm the setup
print_message "$COLOR_GREEN" "$MESSAGE_SETUP_COMPLETE"

# 🧹 Optionally, remove the template repository after setup
rm -rf "$TEMPLATE_DIR"

# 🎉 Done
print_message "$COLOR_GREEN" "$MESSAGE_DONE"