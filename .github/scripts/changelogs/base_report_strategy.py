from base_interfaces import ReportStrategy
from style_config import StyleConfig
from typing import Dict, List, Optional

class BaseReportStrategy(ReportStrategy, StyleConfig):
    """Base class combining ReportStrategy with StyleConfig"""

    def _generate_style_tag(self) -> str:
        type_colors = '\n'.join([
            f'.type-{type} {{ background: {style["color"]}; }}'
            for type, style in self.TYPE_STYLES.items()
        ])
        return f"<style>{self.BASE_STYLES}\n{type_colors}</style>"

    def _generate_header(
            self,
            title: str,
            subtitle: str,
            current_tag: Optional[str] = None,
            previous_tag: Optional[str] = None
    ) -> str:
        """Generate common header markup"""
        return '\n'.join([
            self._generate_style_tag(),
            "<div class='container'>",
            "<header class='header'>",
            f"<h1>{title}</h1>",
            f"<p>{subtitle}</p>",
            f"<p>{f'{previous_tag} -> ' if previous_tag else ''}{current_tag}</p>",
            "</header>"
        ])

    def _generate_type_section(self, type_name: str, commits_by_scope: Dict) -> str:
        """Generate markup for a commit type section"""
        if not commits_by_scope:
            return ""

        emoji = self.TYPE_STYLES[type_name]["emoji"]
        doc = [
            f'<div class="type-header type-{type_name}">',
            f'{emoji} {type_name.capitalize()}s',
            '</div>'
        ]

        for scope, commits in commits_by_scope.items():
            doc.append(self._generate_scope_section(scope, commits))

        return '\n'.join(doc)

    def _generate_scope_section(self, scope: str, commits: List[Dict]) -> str:
        """Generate markup for commits under a scope"""
        return '\n'.join([
            "<details open>",
            f"<summary><span class='scope-tag'>{scope}</span></summary>",
            "<ul class='commit-list'>",
            *[self._generate_commit_item(commit) for commit in commits],
            "</ul>",
            "</details>"
        ])