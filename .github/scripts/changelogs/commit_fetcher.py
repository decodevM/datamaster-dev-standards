# import requests

# from base_interfaces import CommitFetcher
# from typing import Dict, List
# import logging


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# class GitHubCommitFetcher(CommitFetcher):
#     def __init__(self, github_token: str, repo_owner: str, repo_name: str):
#         self.github_token = github_token
#         self.repo_owner = repo_owner
#         self.repo_name = repo_name

#     def fetch_commits(self, branch="main") -> List[Dict]:
#         url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits"
#         headers = {
#             "Authorization": f"token {self.github_token}",
#             "Accept": "application/vnd.github.v3+json"
#         }

#         commits = []
#         page = 1

#         while True:
#             try:
#                 response = requests.get(
#                     url,
#                     headers=headers,
#                     params={"sha": branch, "page": page}
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 if not data:
#                     break
#                 commits.extend(data)
#                 page += 1
#             except Exception as e:
#                 logger.error(f"Error fetching commits: {e}")
#                 break

#         return commits



import requests
from base_interfaces import CommitFetcher
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def get_tags(self) -> List[Dict]:
        """Fetch all tags sorted by creation date"""
        try:
            response = requests.get(
                f"{self.base_url}/tags",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return []

    def get_commits_between_tags(self, base_sha: str, head_sha: str) -> List[Dict]:
        """Get commits between two tags"""
        try:
            response = requests.get(
                f"{self.base_url}/compare/{base_sha}...{head_sha}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('commits', [])
        except Exception as e:
            logger.error(f"Error fetching commits between tags: {e}")
            return []

    def fetch_commits(self, branch="main") -> List[Dict]:
        """Fetch commits based on tags"""
        tags = self.get_tags()
        
        if not tags:
            logger.info("No tags found, fetching all commits")
            return self._fetch_all_commits(branch)
        
        if len(tags) == 1:
            logger.info(f"Found single tag: {tags[0]['name']}")
            return self._fetch_all_commits(branch)
        
        logger.info(f"Found tags: {tags[0]['name']} and {tags[1]['name']}")
        return self.get_commits_between_tags(
            tags[1]['commit']['sha'],  # Previous tag
            tags[0]['commit']['sha']   # Latest tag
        )

    def _fetch_all_commits(self, branch: str) -> List[Dict]:
        """Fetch all commits for a branch"""
        commits = []
        page = 1

        while True:
            try:
                response = requests.get(
                    f"{self.base_url}/commits",
                    headers=self.headers,
                    params={"sha": branch, "page": page}
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                commits.extend(data)
                page += 1
            except Exception as e:
                logger.error(f"Error fetching commits: {e}")
                break

        return commits