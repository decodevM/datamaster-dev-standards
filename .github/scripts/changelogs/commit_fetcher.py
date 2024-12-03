
import requests
from git import Tag, Commit

from base_interfaces import CommitFetcher
from typing import Dict, List, Tuple, Optional, Union
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from git import Repo, Commit
#
# class GitHubCommitFetcher(CommitFetcher):
#     def __init__(self, github_token: str, repo_owner: str, repo_name: str):
#         self.github_token = github_token
#         self.repo_owner = repo_owner
#         self.repo_name = repo_name
#         self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
#         self.headers = {
#             "Authorization": f"token {github_token}",
#             "Accept": "application/vnd.github.v3+json"
#         }
#         self.repo = Repo('.')
#
#     def get_tags(self) -> Tuple[Optional[str], Optional[str]]:
#         """Get latest and previous tags if available"""
#         try:
#             response = requests.get(
#                 f"{self.base_url}/tags",
#                 headers=self.headers
#             )
#             response.raise_for_status()
#             tags = response.json()
#
#             if len(tags) >= 2:
#                 logger.info(f"Found tags: {tags[0]['name']} and {tags[1]['name']}")
#                 return tags[0]['name'], tags[1]['name']
#             elif len(tags) == 1:
#                 logger.info(f"Found single tag: {tags[0]['name']}")
#                 return tags[0]['name'], None
#             else:
#                 logger.info("No tags found")
#                 return None, None
#
#         except Exception as e:
#             logger.error(f"Error fetching tags: {e}")
#             return None, None
#
#     def get_commit_from_tag(self, tag: str) -> Commit:
#         """Get commit object from tag name"""
#         return self.repo.commit(tag)
#
#     def get_commits_between_refs(
#         self,
#         base_ref: Union[Tag, Commit],
#         head_ref: Union[Tag, Commit]
#     ) -> List[Dict]:
#         """Get commits between two refs"""
#         try:
#             base_sha = base_ref.commit.sha if isinstance(base_ref, Tag) else base_ref.hexsha
#             head_sha = head_ref.commit.sha if isinstance(head_ref, Tag) else head_ref.hexsha
#
#             logger.info(f"Comparing {base_sha[:7]} to {head_sha[:7]}")
#
#             response = requests.get(
#                 f"{self.base_url}/compare/{base_sha}...{head_sha}",
#                 headers=self.headers
#             )
#             response.raise_for_status()
#             return response.json().get('commits', [])
#
#         except Exception as e:
#             logger.error(f"Error fetching commits between refs: {e}")
#             return []
#
#     def fetch_commits(self, branch="main") -> List[Dict]:
#         """Fetch commits between the latest two tags or all commits if only one tag exists"""
#         latest_tag, previous_tag = self.get_tags()
#
#         if latest_tag and previous_tag:
#             latest_commit = self.get_commit_from_tag(latest_tag)
#             previous_commit = self.get_commit_from_tag(previous_tag)
#             return self.get_commits_between_refs(previous_commit, latest_commit)
#         elif latest_tag:
#             latest_commit = self.get_commit_from_tag(latest_tag)
#             return self.get_commits_between_refs(Commit(self.repo, 'HEAD'), latest_commit)
#         else:
#             return self.get_commits_between_refs(Commit(self.repo, 'HEAD'), Commit(self.repo, 'HEAD'))





class GitHubCommitFetcher(CommitFetcher):
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.repo = Repo('.')

    def get_tags(self) -> Tuple[Optional[str], Optional[str]]:
        """Get latest and previous tags if available"""
        try:
            response = requests.get(
                f"{self.base_url}/tags",
                headers=self.headers
            )
            response.raise_for_status()
            tags = response.json()

            if len(tags) >= 2:
                logger.info(f"Found tags: {tags[0]['name']} and {tags[1]['name']}")
                return tags[0]['name'], tags[1]['name']
            elif len(tags) == 1:
                logger.info(f"Found single tag: {tags[0]['name']}")
                return tags[0]['name'], None
            else:
                logger.info("No tags found")
                return None, None

        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return None, None

    def get_commit_from_tag(self, tag: str) -> Commit:
        """Get commit object from tag name"""
        return self.repo.commit(tag)

    def get_commits_between_refs(
        self,
        base_ref: Union[Tag, Commit],
        head_ref: Union[Tag, Commit]
    ) -> List[Dict]:
        """Get commits between two refs"""
        try:
            base_sha = base_ref.commit.sha if isinstance(base_ref, Tag) else base_ref.hexsha
            head_sha = head_ref.commit.sha if isinstance(head_ref, Tag) else head_ref.hexsha

            logger.info(f"Comparing {base_sha[:7]} to {head_sha[:7]}")

            response = requests.get(
                f"{self.base_url}/compare/{base_sha}...{head_sha}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('commits', [])

        except Exception as e:
            logger.error(f"Error fetching commits between refs: {e}")
            return []

    def fetch_commits(self, branch="main") -> List[Dict]:
        """Fetch commits between the latest two tags or all commits if only one tag exists"""
        latest_tag, previous_tag = self.get_tags()

        if latest_tag and previous_tag:
            latest_commit = self.get_commit_from_tag(latest_tag)
            previous_commit = self.get_commit_from_tag(previous_tag)
            return self.get_commits_between_refs(previous_commit, latest_commit)
        elif latest_tag:
            latest_commit = self.get_commit_from_tag(latest_tag)
            initial_commit = self.repo.iter_commits().next()  # Get the initial commit
            return self.get_commits_between_refs(initial_commit, latest_commit)
        else:
            return self.get_commits_between_refs(self.repo.commit('HEAD'), self.repo.commit('HEAD'))