import os
from base_report_strategy import BaseReportStrategy
from typing import Dict, Optional
from datetime import datetime

class MarkdownCommitReportGenerator(BaseReportStrategy):

    def _generate_empty_state(self) -> str:
        """Generate markup for when there are no commits"""
        return """<div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>No Changes Found</h3>
                <p>There are no commits between these tags.</p>
            </div>
        """

    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a single commit"""
        elements = [
            "<li class='commit-item'>",
            f"<div class='commit-title'>{commit['title']}</div>",
            f"<div class='commit-meta'>👤 {commit['author']} • 📅 {commit['date']}</div>"
        ]

        if commit['body']:
            elements.extend([
                "<div class='commit-body'>",
                commit['body'],
                "</div>"
            ])

        if commit['refs']:
            elements.append(f"<div class='commit-meta'>🔗 {', '.join(commit['refs'])}</div>")

        elements.append("</li>")
        return '\n'.join(elements)

    def generate(
            self,
            commits: Dict,
            current_tag: Optional[str] = None,
            previous_tag: Optional[str] = None
    ) -> str:
        today = datetime.now().strftime("%d %B %Y")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = [
            "<!DOCTYPE html>",
            "<html lang='en'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            "<title>Commit Report</title>",
            """<link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;700&display=swap" rel="stylesheet">"""
            "</head>",
            "<body>",
            self._generate_header(
                title="📄Commit Report",
                subtitle=f"Generated on {today}",
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
                doc.append(self._generate_type_section(type_name, commits.get(type_name, {})))

        doc.append("</div>")
        doc.append("</body>")
        doc.append("</html>")

        # Ensure all elements are strings
        return '\n'.join(map(str, doc))