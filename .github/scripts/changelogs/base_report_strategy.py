from base_interfaces import ReportStrategy, StyleConfig
from typing import Dict, List

class BaseReportStrategy(ReportStrategy, StyleConfig):
    """Base class combining ReportStrategy with StyleConfig"""
    
    def _generate_style_tag(self) -> str:
        type_colors = '\n'.join([
            f'.type-{type} {{ background: {style["color"]}; }}'
            for type, style in self.TYPE_STYLES.items()
        ])
        return f"<style>{self.BASE_STYLES}\n{type_colors}</style>"

    def _generate_header(self, title: str, subtitle: str) -> List[str]:
        """Generate common header markup"""
        return [
            self._generate_style_tag(),
            "<div class='container'>",
            "<header class='header'>",
            f"<h1>{title}</h1>",
            f"<p>{subtitle}</p>",
            "</header>"
        ]

    def _generate_type_section(self, type_name: str, commits_by_scope: Dict) -> List[str]:
        """Generate markup for a commit type section"""
        if not commits_by_scope:
            return []

        emoji = self.TYPE_STYLES[type_name]["emoji"]
        doc = [
            f'<div class="type-header type-{type_name}">'
            f'{emoji} {type_name.capitalize()}s'
            '</div>'
        ]

        for scope, commits in commits_by_scope.items():
            doc.extend(self._generate_scope_section(scope, commits))
        
        return doc

    def _generate_scope_section(self, scope: str, commits: List[Dict]) -> List[str]:
        """Generate markup for commits under a scope"""
        return [
            "<details open>",
            f"<summary><span class='scope-tag'>{scope}</span></summary>",
            "<ul class='commit-list'>",
            *[self._generate_commit_item(commit) for commit in commits],
            "</ul>",
            "</details>"
        ]