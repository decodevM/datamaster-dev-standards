
from base_report_strategy import BaseReportStrategy
from datetime import datetime
from typing import Dict, Optional

class ReleaseChangelogReportGenerator(BaseReportStrategy):

    def _generate_empty_state(self) -> str:
        """Generate markup for when there are no commits"""
        return """
        <div class="empty-state">
            <div class="empty-icon">🔍</div>
            <h3>No Changes Found</h3>
            <p>There are no commits between these tags.</p>
        </div>
        """


    def _generate_commit_item(self, commit: Dict) -> str:
        """Generate markup for a release commit item"""
        
        message = f"{commit['title']}\n{commit['body']}" if commit['body'] else commit['title']

        elements = ["<li class='commit-item'>", 
                    self.generate_copy_button(message),
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
        """Generate release changelog HTML"""
        
        version, today = self._generate_version_info()
        
        # Generate header
        doc = self._generate_header(
            title=f"🚀 Release {version}",
            subtitle=f"Released on {today}",
            latest_tag=current_tag,
            previous_tag=previous_tag
        )

         # Check if there are any commits
        has_commits = any(commits.get(type_name) for type_name in self.PRIORITY_ORDER)
        
        if not has_commits:
            doc.append(self._generate_empty_state())
        else:
                    # Generate sections for each commit type
            for type_name in self.PRIORITY_ORDER:
                doc.extend(self._generate_type_section(
                    type_name, 
                    commits.get(type_name, {})
                ))

        doc.append("</div>")
        return '\n'.join(doc)