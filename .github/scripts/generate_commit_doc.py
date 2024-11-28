import os
import subprocess
from collections import defaultdict

# Mapping commit types to document sections
COMMIT_SECTIONS = {
    "fix": "Corrections de Bugs",
    "feat": "Évolutions",
    # Add more mappings as needed
}

def parse_commit_message(commit):
    """
    Parse a commit message into type, scope, and description.
    """
    parts = commit.split(": ", 1)
    if len(parts) < 2:
        return None  # Skip invalid formats

    header, description = parts
    type_and_scope = header.split("(", 1)
    commit_type = type_and_scope[0].strip()
    scope = type_and_scope[1].rstrip(")") if len(type_and_scope) > 1 else None

    return {
        "type": commit_type,
        "scope": scope,
        "description": description.strip(),
    }

def generate_commit_document():
    # Ensure the output directory exists
    output_directory = "generated_docs"
    os.makedirs(output_directory, exist_ok=True)

    # File path for the commit document
    output_file = os.path.join(output_directory, "commit_document.txt")

    try:
        # Fetch commits from the current push only
        result = subprocess.run(
            ["git", "log", "HEAD^..HEAD", "--pretty=format:%s%n%b"],
            stdout=subprocess.PIPE,
            text=True,
        )

        commits = result.stdout.strip().split("\n\n")
        grouped_commits = defaultdict(list)

        # Parse commits and group them by type
        for raw_commit in commits:
            parsed_commit = parse_commit_message(raw_commit)
            if parsed_commit:
                section = COMMIT_SECTIONS.get(parsed_commit["type"], "Autres")
                grouped_commits[section].append(parsed_commit)

        # Write the document
        with open(output_file, "w") as file:
            file.write("Rapport des Commits\n")
            file.write("=" * 50 + "\n")
            file.write(f"Client : [Nom du Client]\n")
            file.write(f"Date : {os.popen('date "+%d %B %Y"').read().strip()}\n")
            file.write("=" * 50 + "\n\n")

            for section, commits in grouped_commits.items():
                file.write(f"II. {section}\n")
                for i, commit in enumerate(commits, 1):
                    scope_text = f"[{commit['scope']}]" if commit['scope'] else ""
                    file.write(f"• {section.split(' ')[0]} {i}: {scope_text} {commit['description']}\n")
                file.write("\n")

        print(f"Commit document created at {output_file}")

    except Exception as e:
        print(f"An error occurred while generating the commit document: {e}")

if __name__ == "__main__":
    generate_commit_document()