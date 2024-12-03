# import os
# import logging
# from typing import Optional, Tuple

# from base_interfaces import CommitFetcher, CommitParser
# from commit_document_manager import CommitDocumentManager
# from report_generator_factory import ReportGeneratorFactory
# from datetime import datetime

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# class EnhancedCommitDocumentManager(CommitDocumentManager):
#     def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
#         super().__init__(commit_fetcher, commit_parser)
#         self.reports = {}
        
#         # Get workspace root directory
#         self.workspace_root = os.getenv('GITHUB_WORKSPACE', os.getcwd())
#         self.output_dir = os.path.join(self.workspace_root, 'generated_docs')
        
#         # Ensure output directory exists
#         os.makedirs(self.output_dir, exist_ok=True)
#         logger.info(f"Output directory set to: {self.output_dir}")

#     def _get_tag_info(self) -> Tuple[Optional[str], Optional[str]]:
#         """Get current and previous tag information"""
#         try:
#             current_tag, previous_tag = self.commit_fetcher.get_tags_or_commits()
            
#             if hasattr(current_tag, 'name'):  # If it's a Tag object
#                 current_tag_name = current_tag.name
#             else:  # If it's a Commit object
#                 current_tag_name = current_tag.sha[:7]

#             if hasattr(previous_tag, 'name'):
#                 previous_tag_name = previous_tag.name
#             else:
#                 previous_tag_name = previous_tag.sha[:7]

#             logger.info(f"Found tags/refs: {current_tag_name} -> {previous_tag_name}")
#             return current_tag_name, previous_tag_name
            
#         except Exception as e:
#             logger.warning(f"Error getting tags: {e}")
#             return None, None

#     def generate_all_documents(self):
#         commits = self.commit_fetcher.fetch_commits()
#         categorized = self.categorize_commits(commits)
        
#         current_tag, previous_tag = self._get_tag_info()

#         generators = {
#             'release_notes': ReportGeneratorFactory.create_generator('release'),
#             'commit_report': ReportGeneratorFactory.create_generator('markdown')
#         }

#         for report_name, generator in generators.items():
#             content = generator.generate(
#                 commits=categorized,
#                 current_tag=current_tag,
#                 previous_tag=previous_tag
#             )
#             self.save_document(content, f"generated_docs/{report_name}.md")

#     def save_document(self, content: str, base_filename: str):
#         filename = f"{os.path.splitext(base_filename)[0]}_{datetime.now().strftime('%Y-%m-%d')}.md"
#         os.makedirs(os.path.dirname(filename), exist_ok=True)
        
#         with open(filename, 'w', encoding='utf-8') as file:
#             file.write(content)
#         logger.info(f"✅ Generated {filename}")




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
            current_tag, previous_tag = self.commit_fetcher.get_tags()

            # Get tag names or SHA if tags are commits
            current_ref = current_tag.name if hasattr(current_tag, 'name') else current_tag.sha[
                                                                                :7] if current_tag else None
            previous_ref = previous_tag.name if hasattr(previous_tag, 'name') else previous_tag.sha[
                                                                                   :7] if previous_tag else None

            logger.info(f"Using refs: {current_ref} -> {previous_ref}")

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
                content = generator.generate(
                    commits=categorized,
                    current_tag=current_ref,
                    previous_tag=previous_ref
                )
                self.save_document(content, f"{report_name}.md")

            # Verify files were created
            files = list(Path(self.output_dir).glob('*.md'))
            logger.info(f"Generated {len(files)} files: {[f.name for f in files]}")

        except Exception as e:
            logger.error(f"❌ Error generating documents: {e}")
            raise

    def save_document(self, content: str, base_filename: str):
        filename = os.path.join(self.output_dir,
                                f"{os.path.splitext(base_filename)[0]}_{datetime.now().strftime('%Y-%m-%d')}.md")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"✅ Generated {filename}")