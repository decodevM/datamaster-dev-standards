
# Define styled output helpers
RED="\033[1;31m"
GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
MAGENTA="\033[1;35m"
WHITE="\033[1;37m"
RESET="\033[0m"
BOLD="\033[1m"

# Define type and scope options in arrays
TYPES=("feat" "fix" "docs" "style" "refactor" "perf" "test" "chore")


# Dynamic horizontal line for styling
print_line() {
  local length="$1"
  printf "${WHITE}%*s\n" $((length + 1)) | tr " " "="
}


print_commit_requirements(){
    local error_message="${1}"
    local tip_message="${2}"
     # Invalid commit message
    message="Commit message requirements:"
    print_line ${#message}
    echo -e "${YELLOW}${message}${RESET}"
    print_line ${#message}
  
    # Commit message format explanation
    echo -e "${BLUE}  ✅ Format: <type>(<scope>): <short description>${RESET}"
    echo -e "${BLUE}    - <type>: One of ($(IFS=\,; echo "${TYPES[*]}"))${RESET}"
    printf "\n"
    echo -e "${BLUE}    - <scope>: One of:${RESET}"
      for scope in "${SCOPES[@]}"; do
        echo -e "${BLUE}      - ${scope}${RESET}"
      done
    printf "\n"
    echo -e "${BLUE}    - <description>: Starts with uppercase, max $SHORT_DESC_LENGTH chars${RESET}\n"
    echo -e "${BLUE}  Body (optional): Detailed change description (multiline supported).${RESET}\n"
    echo -e "${BLUE}  Footer (optional): ${REFS_REGEX}${RESET}\n"

    # Examples
    echo -e "${MAGENTA}${BOLD}Examples:${RESET}\n"
    echo -e "${RED}  ❌ add user authentication feature${RESET}\n"
    echo -e "${GREEN}  ✅ feat(Authentication): Add user authentication feature${RESET}"
    echo -e "${GREEN}     Implemented a secure flow.${RESET}"
    echo -e "${GREEN}     Refs: #CU-12345${RESET}\n"
    echo -e "${GREEN}  ✅ fix(API): Resolve API endpoint errors${RESET}"
    echo -e "${GREEN}     Fixed timeout issues in user endpoints.${RESET}"
    echo -e "${GREEN}     Refs: #CU-67890${RESET}\n"
    echo -e "${GREEN}  ✅ test(Database): Add tests for database migrations${RESET}"
    echo -e "${GREEN}     Verified integrity during schema updates.${RESET}"
    echo -e "${GREEN}     Refs: #CU-98765${RESET}\n"

    # Tip for modification
    print_line ${#TIP_MSG}
    echo -e "${YELLOW}${BOLD}$TIP_MSG${RESET}"
    print_line ${#TIP_MSG}

    printf "\n"

    # Final error message
    print_line ${#error_message}
    echo -e "${RED}${BOLD}$error_message${RESET}"
    if [ -n "$tip_message" ]; then
        printf "\n"
        echo -e "${YELLOW}${tip_message}${RESET}"
        print_line ${#tip_message}
    else
    print_line ${#error_message}
    fi
}


# Constants
SHORT_DESC_LENGTH=120
SUCCESS_MSG="✅ SUCCESS: Your commit message follows the correct format."
ERROR_MSG="❌ ERROR: Commit message does not follow the required format."
EMPTY_MSG="❌ ERROR: Commit message is empty."
TIP_MSG="💡 Tip: Use \`git commit --amend\` to modify your commit message."
MISSING_SHORT_DESC="❌ ERROR: Short description is missing or improperly formatted."
SHORT_DESC_LIMIT="❌ ERROR: Short description exceeds limit characters."
INVALID_COMMIT_TYPE="❌ ERROR: Invalid commit type."
INVALID_COMMIT_SCOPE="❌ ERROR: Invalid commit scope."
MISSING_COMMIT_SCOPE="❌ ERROR: Commit scope is missing."
INVALID_REFS_ID="❌ ERROR: Invalid 'Refs' line."
INVALID_SHORT_DESC_CAPITAL="❌ ERROR: Short description should start with a capital letter."
SHORT_DESC_TIP_MSG="💡 Tip: Consider shortening your description to fit within the limit."



# Generate type and scope regex dynamically (no trailing or leading spaces)
TYPE_REGEX=$(IFS=\|; echo "${TYPES[*]}")
SCOPE_REGEX=$(IFS=\|; echo "${SCOPES[*]}")

SHORT_DESC_REGEX=".*"  # Matches the short description after the colon
MULTILINE_DESC_REGEX="[\s\S]+"  # Matches multiline description if any
REFS_REGEX="Refs: #[A-Za-z0-9-]+"  # Refs line regex

# Combine regex for full commit message validation
COMMIT_MSG_PATTERN="^($TYPE_REGEX)\(($SCOPE_REGEX)\):\s*($SHORT_DESC_REGEX)(\s*$MULTILINE_DESC_REGEX)?\s*($REFS_REGEX)?$"
# COMMIT_MSG_PATTERN="^($TYPE_REGEX)\(($SCOPE_REGEX)\):\s*($SHORT_DESC_REGEX)(\s*$MULTILINE_DESC_REGEX)?\s*$REFS_REGEX$"


# Read the commit message (file or input string)
if [ -f "$1" ]; then
  COMMIT_MSG=$(<"$1")
elif [ -n "$1" ]; then
  COMMIT_MSG="$1"
else
    print_commit_requirements "${EMPTY_MSG}"
  exit 1
fi

# Ensure the commit message is not empty
if [[ -z "$COMMIT_MSG" ]]; then
    print_commit_requirements "${EMPTY_MSG}"
    exit 1
fi


# Validate the type
validate_commit_type() {
  # Extract the type (requires the presence of a scope)
  TYPE=$(echo "$COMMIT_MSG" | sed -n 's/^\([a-zA-Z]*\)([^)]*):.*/\1/p')

  # Check if type is valid
  if [[ -z "$TYPE" || ! " ${TYPES[@]} " =~ " ${TYPE} " ]]; then
    print_commit_requirements "${INVALID_COMMIT_TYPE}"
    exit 1
  fi

  SCOPE=$(echo "$COMMIT_MSG" | sed -n 's/^[a-zA-Z]*(\([^)]*\)):.*$/\1/p')
  if [[ -z "$SCOPE" ]]; then
    print_commit_requirements "${MISSING_COMMIT_SCOPE}"
    exit 1
  fi

  # Ensure a scope exists

}

# Validate the scope
validate_commit_scope() {
  # Extract the scope (if any)
  SCOPE=$(echo "$COMMIT_MSG" | sed -n 's/^[a-zA-Z]*(\([^)]*\)):.*$/\1/p')

  # If the scope is not empty, validate it against the allowed list
  if [[ -n "$SCOPE" && ! " ${SCOPES[@]} " =~ " ${SCOPE} " ]]; then
    print_commit_requirements "${INVALID_COMMIT_SCOPE}"
    exit 1
  fi

  # If the scope is empty, it's valid since it's optional
}

validate_short_desc() {

  # Extract short description
  SHORT_DESC=$(echo "$COMMIT_MSG" | sed -n 's/^[^:]*: \(.*\)$/\1/p' | head -n 1)

  # Validate short description
  if [[ -z "$SHORT_DESC" ]]; then
    print_commit_requirements "${MISSING_SHORT_DESC}"
    exit 1
  fi

  # Validate short description starts with a capital letter
  validate_short_desc_capital() {
    if [[ ! "$SHORT_DESC" =~ ^[A-Z] ]]; then
      print_commit_requirements "${INVALID_SHORT_DESC_CAPITAL}"
      exit 1
    fi
  }

  # Check if short description exceeds the limit
  check_short_desc_length() {
    if (( ${#SHORT_DESC} > $SHORT_DESC_LENGTH )); then    
      print_commit_requirements "${SHORT_DESC_LIMIT}" "${SHORT_DESC_TIP_MSG}"
      exit 1
    fi
  }

}

# Validate refs line (optional)
validate_refs_line() {
  # Extract the refs line (if any)
  if [[ "$COMMIT_MSG" =~ $REFS_REGEX ]]; then
    # If refs are present but invalid, show an error
    if [[ ! "$COMMIT_MSG" =~ $REFS_REGEX ]]; then
      print_commit_requirements "${INVALID_REFS_ID}"
      exit 1
    fi
  fi

  # If refs are not present, it's valid since it's optional
}

# Validate full commit message format using regex
validate_commit_message() {
  if [[ "$COMMIT_MSG" =~ $COMMIT_MSG_PATTERN ]]; then
    print_line ${#SUCCESS_MSG}
    echo -e "${GREEN}${BOLD}$SUCCESS_MSG${RESET}"
    print_line ${#SUCCESS_MSG}
    exit 0
  else
    print_commit_requirements "${ERROR_MSG}"
    exit 1
  fi
}

# Run validations
validate_commit_type
validate_commit_scope
validate_short_desc
validate_short_desc_capital
check_short_desc_length
validate_refs_line
validate_commit_message
