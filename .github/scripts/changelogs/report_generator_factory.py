from markdown_commit_report_generator import MarkdownCommitReportGenerator
from release_changelog_report_generator import ReleaseChangelogReportGenerator
from base_interfaces import ReportStrategy

class ReportGeneratorFactory:
    @staticmethod
    def create_generator(report_type: str) -> ReportStrategy:
        generators = {
            'release': ReleaseChangelogReportGenerator(),
            'markdown': MarkdownCommitReportGenerator()
        }
        return generators.get(report_type)
