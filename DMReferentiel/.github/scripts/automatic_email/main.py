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

    # Define a dictionary to map repository names to application names
    REPO_APP_MAPPING = {
        "datamaster-dev-standards": "DataMaster Dev Standards",
        "DMAdministration": "Administration",
        "DMDashbord": "Dashboard",
        "DMExpoImpo": "Import et Export",
        "DMInventorying": "Stock",
        "DMPriceViewer": "Price Viewer",
        "DMReferentiel": "Referentiel",
        "DMSPOS": "POS",
        "DMSPurchase": "Commercial",
        "DMSTASK": "TASK",
        "TaskWeb": "TASK Web",
        # Add more mappings as needed
    }

    # Get the repository name from the environment
    repo_name = os.getenv("REPO_NAME", "Unknown Repository")

    # Get the application name based on the repository name
    app_name = REPO_APP_MAPPING.get(repo_name, "Unknown")

    context = {
        "appName": app_name,
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