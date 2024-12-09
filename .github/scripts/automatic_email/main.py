import os
from datetime import datetime

def populate_email_template(template_path, output_path, context):
    # Read the template
    with open(template_path, 'r') as file:
        template = file.read()

    # Replace placeholders with context data
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", value)

    # Write the populated template to a new file
    with open(output_path, 'w') as file:
        file.write(template)

if __name__ == "__main__":
    # Environment variables for dynamic data
    context = {
        "repoName": os.getenv("REPO_NAME", "Unknown Repository"),
        "tagName": os.getenv("TAG_NAME", "Unknown Tag"),
        "date": datetime.now().strftime('%Y-%m-%d'),
        "year": datetime.now().strftime('%Y')
    }

    # Template file paths
    template_path = ".github/scripts/automatic_email/email_template.html"
    output_path = ".github/scripts/automatic_email/email_output.html"

    # Populate and save the template
    populate_email_template(template_path, output_path, context)
    print(f"Populated email saved to {output_path}")