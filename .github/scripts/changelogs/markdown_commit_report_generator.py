import os

from  base_report_strategy import  BaseReportStrategy
from typing import Dict
from datetime import datetime

class MarkdownCommitReportGenerator(BaseReportStrategy):
    def _generate_commit_item(self, commit: Dict) -> str:
        
        """Generate markup for a single commit"""
        
        message = f"{commit['title']}\n{commit['body']}" if commit['body'] else commit['title']
        
        elements = [
            "<li class='commit-item'>",
            self.generate_copy_button(message),
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

    def generate(self, commits: Dict) -> str:
        today = datetime.now().strftime("%d %B %Y")
        repo_info = f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}"

        doc = self._generate_header(
            title="📄 Commit Report",
            subtitle=f"Generated on {today}"
        )

        for type_name in self.PRIORITY_ORDER:
            doc.extend(self._generate_type_section(type_name, commits.get(type_name, {})))

        doc.append("</div>")
        return '\n'.join(doc)