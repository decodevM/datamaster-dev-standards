
from base_report_strategy import BaseReportStrategy
from datetime import datetime
from typing import Dict

class ReleaseChangelogReportGenerator(BaseReportStrategy):
    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a release commit item"""
        elements = ["<li class='commit-item'>", f"<div class='commit-title'>{commit['title']}</div>", "</li>"]
        return '\n'.join(elements)

    def _generate_version_info(self) -> tuple[str, str]:
        """Generate version and date strings"""
        today = datetime.now().strftime("%d %B %Y")
        version = datetime.now().strftime("v%Y.%m.%d")
        return version, today

    def generate(self, commits: Dict) -> str:
        """Generate release changelog HTML"""
        version, today = self._generate_version_info()
        
        # Generate header
        doc = self._generate_header(
            title=f"🚀 Release {version}",
            subtitle=f"Released on {today}"
        )

        # Generate sections for each commit type
        for type_name in self.PRIORITY_ORDER:
            doc.extend(self._generate_type_section(
                type_name, 
                commits.get(type_name, {})
            ))

        doc.append("</div>")
        return '\n'.join(doc)
