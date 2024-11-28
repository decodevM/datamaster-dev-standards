import os
import subprocess

def generate_commit_document():
    # Ensure the output directory exists
    output_directory = "generated_docs"
    os.makedirs(output_directory, exist_ok=True)

    # File path for the commit document
    output_file = os.path.join(output_directory, "commit_document.txt")

    try:
        # Run the git log command to get commit history
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h | %an | %ad | %s", "--date=short"],
            stdout=subprocess.PIPE,
            text=True,
        )

        # Write the commit history to a file
        with open(output_file, "w") as file:
            file.write("Commit History Document\n")
            file.write("=" * 50 + "\n")
            file.write("Format: <Commit Hash> | <Author> | <Date> | <Message>\n\n")
            file.write(result.stdout)

        print(f"Commit document created at {output_file}")

    except Exception as e:
        print(f"An error occurred while generating the commit document: {e}")

if __name__ == "__main__":
    generate_commit_document()