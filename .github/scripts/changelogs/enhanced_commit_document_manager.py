
# from weasyprint import HTML
import subprocess
import os
import logging
from pathlib import Path
from commit_document_manager import CommitDocumentManager
from base_interfaces import CommitFetcher, CommitParser
from datetime import datetime
from report_generator_factory import ReportGeneratorFactory


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedCommitDocumentManager(CommitDocumentManager):
    def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
        super().__init__(commit_fetcher, commit_parser)
        self.reports = {}
        # Get workspace root directory
        self.workspace_root = os.getenv('GITHUB_WORKSPACE', os.getcwd())
        self.output_dir = os.path.join(self.workspace_root, 'generated_docs')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")


    def generate_all_documents(self):
        try:
            # Get tags first
            current_tag_name, previous_tag_name = self.commit_fetcher.get_tags()

            # Convert tag names to Commit objects
            current_tag = self.commit_fetcher.get_commit_from_tag(current_tag_name) if current_tag_name else None
            previous_tag = self.commit_fetcher.get_commit_from_tag(previous_tag_name) if previous_tag_name else None

            logger.info(f"Using refs: {current_tag_name} -> {previous_tag_name}")

            # Get commits between tags if available
            if current_tag and previous_tag:
                commits = self.commit_fetcher.get_commits_between_refs(previous_tag, current_tag)
            else:
                commits = self.commit_fetcher.fetch_commits()

            categorized = self.categorize_commits(commits)

            generators = {
                'release_notes': ReportGeneratorFactory.create_generator('release'),
                'commit_report': ReportGeneratorFactory.create_generator('markdown')
            }

            logger.info(f"Generating documents in: {self.output_dir}")

            for report_name, generator in generators.items():
                # Generate HTML content
                content = generator.generate(
                    commits=categorized,
                    current_tag=current_tag_name,
                    previous_tag=previous_tag_name
                )
                # self.save_document(content, f"generated_docs/{report_name}.html")
                html_file = self.save_document(content, f"{report_name}.html")

                # Generate corresponding PDF file
                self.generate_pdf(html_file)

            # Verify files were created
            files = list(Path(self.output_dir).glob('*.html'))
            logger.info(f"Generated {len(files)} files: {[f.name for f in files]}")

        except Exception as e:
            logger.error(f"❌ Error generating documents: {e}")
            raise

    def save_document(self, content: str, base_filename: str):
        """Save HTML content to a file and return the file path."""
        filename = os.path.join(self.output_dir,
                                f"{os.path.splitext(base_filename)[0]}_{datetime.now().strftime('%Y-%m-%d')}.html")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)

        logger.info(f"✅ Generated {filename}")
        return filename



    # def generate_pdf(self, html_file: str):
    #     """Generate a PDF from the given HTML file using pdfkit."""
    #     try:
    #         pdf_file = os.path.splitext(html_file)[0] + '.pdf'
    #         pdfkit.from_file(html_file, pdf_file)
    #         logger.info(f"✅ Generated PDF: {pdf_file}")
    #     except Exception as e:
    #         logger.error(f"❌ Error generating PDF for {html_file}: {e}")
    #         raise


    def generate_pdf(self, html_file: str):
        """
        Generate a PDF from the given HTML file using wkhtmltopdf.
        This ensures that the PDF matches the rendered HTML appearance.
        """
        try:
            # Define the output PDF file name
            pdf_file = os.path.splitext(html_file)[0] + '.pdf'
            
            # Command to use wkhtmltopdf
            command = [
                "wkhtmltopdf",
                "--enable-local-file-access",  # Allow access to local files
                "--print-media-type",  # Use @media print styles
                "--no-stop-slow-scripts",  # Allow rendering of dynamic content
                html_file,
                pdf_file
            ]
            
            # Execute the command
            subprocess.run(command, check=True)
            
            logger.info(f"Generated PDF: {pdf_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating PDF for {html_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise