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
from typing import Dict, List, Tuple, Optional, Union
from github import Tag, Commit
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

    def get_tags(self) -> Tuple[Optional[Tag], Optional[Tag]]:
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
                return Tag(tags[0]), Tag(tags[1])
            elif len(tags) == 1:
                logger.info(f"Found single tag: {tags[0]['name']}")
                return Tag(tags[0]), None
            else:
                logger.info("No tags found")
                return None, None

        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return None, None

    def get_commits_between_refs(
        self,
        base_ref: Union[Tag, Commit],
        head_ref: Union[Tag, Commit]
    ) -> List[Dict]:
        """Get commits between two refs"""
        try:
            base_sha = base_ref.commit.sha if isinstance(base_ref, Tag) else base_ref.sha
            head_sha = head_ref.commit.sha if isinstance(head_ref, Tag) else head_ref.sha

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
        """Fetch all commits from repository"""
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