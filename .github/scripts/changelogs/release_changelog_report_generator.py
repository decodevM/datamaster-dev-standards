from base_report_strategy import BaseReportStrategy
from datetime import datetime
from typing import Dict, Optional

class ReleaseChangelogReportGenerator(BaseReportStrategy):

    def _generate_empty_state(self) -> str:
        """Generate markup for when there are no commits"""
        return """<div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>No Changes Found</h3>
                <p>There are no commits between these tags.</p>
            </div>
        """

    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a release commit item"""
        elements = ["<li class='commit-item'>",
                    f"<div class='commit-title'>{commit['title']}</div>",
                    "</li>"]
        return '\n'.join(elements)

    def _generate_version_info(self) -> tuple[str, str]:
        """Generate version and date strings"""
        today = datetime.now().strftime("%d %B %Y")
        version = datetime.now().strftime("v%Y.%m.%d")
        return version, today

    def generate(
            self,
            commits: Dict,
            current_tag: Optional[str] = None,
            previous_tag: Optional[str] = None
    ) -> str:
        version, today = self._generate_version_info()

        # Generate header
        doc = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>Release</title>",
            "</head>",
            "<body>",
            self._generate_header(
                title=f"🚀 Release",
                subtitle=f"Released on {today}",
                current_tag=current_tag,
                previous_tag=previous_tag
            )
        ]

        # Check if there are any commits
        has_commits = any(commits.get(type_name) for type_name in self.PRIORITY_ORDER)

        if not has_commits:
            doc.append(self._generate_empty_state())
        else:
            for type_name in self.PRIORITY_ORDER:
                doc.append(self._generate_type_section(
                    type_name,
                    commits.get(type_name, {})
                ))

        doc.append("</div>")
        doc.append("</body>")
        doc.append("</html>")

        # Ensure all elements are strings
        return '\n'.join(map(str, doc))