import os
import logging
from typing import Optional, Tuple

from base_interfaces import CommitFetcher, CommitParser
from commit_document_manager import CommitDocumentManager
from report_generator_factory import ReportGeneratorFactory
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedCommitDocumentManager(CommitDocumentManager):
    def __init__(self, commit_fetcher: CommitFetcher, commit_parser: CommitParser):
        super().__init__(commit_fetcher, commit_parser)
        self.reports = {}

    def _get_tag_info(self) -> Tuple[Optional[str], Optional[str]]:
        """Get current and previous tag information"""
        try:
            current_tag, previous_tag = self.commit_fetcher.get_tags_or_commits()
            
            if hasattr(current_tag, 'name'):  # If it's a Tag object
                current_tag_name = current_tag.name
            else:  # If it's a Commit object
                current_tag_name = current_tag.sha[:7]

            if hasattr(previous_tag, 'name'):
                previous_tag_name = previous_tag.name
            else:
                previous_tag_name = previous_tag.sha[:7]

            logger.info(f"Found tags/refs: {current_tag_name} -> {previous_tag_name}")
            return current_tag_name, previous_tag_name
            
        except Exception as e:
            logger.warning(f"Error getting tags: {e}")
            return None, None

    def generate_all_documents(self):
        commits = self.commit_fetcher.fetch_commits()
        categorized = self.categorize_commits(commits)
        
        current_tag, previous_tag = self._get_tag_info()

        generators = {
            'release_notes': ReportGeneratorFactory.create_generator('release'),
            'commit_report': ReportGeneratorFactory.create_generator('markdown')
        }

        for report_name, generator in generators.items():
            content = generator.generate(
                commits=categorized,
                current_tag=current_tag,
                previous_tag=previous_tag
            )
            self.save_document(content, f"generated_docs/{report_name}.md")

    def save_document(self, content: str, base_filename: str):
        filename = f"{os.path.splitext(base_filename)[0]}_{datetime.now().strftime('%Y-%m-%d')}.md"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        logger.info(f"✅ Generated {filename}")