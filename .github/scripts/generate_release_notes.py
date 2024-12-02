import os
import requests
from datetime import datetime
from github import Github
from github.Tag import Tag
from github.Commit import Commit

def get_ref_sha(ref) -> str:
    """Get SHA from either Tag or Commit object"""
    if isinstance(ref, Tag):
        return ref.commit.sha
    return ref.sha

def get_tags_or_commits():
    """Get latest tags or use commits if no/single tag exists"""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}")
    
    tags = list(repo.get_tags())
    
    if len(tags) >= 2:
        print(f"Found multiple tags: {tags[0].name} and {tags[1].name}")
        return tags[0], tags[1]
    elif len(tags) == 1:
        print(f"Found single tag: {tags[0].name}")
        commits = list(repo.get_commits(sha=tags[0].commit.sha + "^"))
        if commits:
            previous_commit = commits[min(10, len(commits)-1)]
            print(f"Using commit {previous_commit.sha[:7]} as previous reference")
            return tags[0], previous_commit
    
    commits = list(repo.get_commits())
    if len(commits) >= 2:
        print("No tags found, using latest commits instead")
        latest = commits[0]
        previous = commits[min(10, len(commits)-1)]
        return latest, previous
    
    print("Not enough history found")
    return None, None

def get_commits_between_refs(latest_ref, previous_ref):
    """Get commits between two refs (tags or commits)"""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}")
    
    latest_sha = get_ref_sha(latest_ref)
    previous_sha = get_ref_sha(previous_ref)
    
    print(f"Comparing {previous_sha[:7]} to {latest_sha[:7]}")
    comparison = repo.compare(previous_sha, latest_sha)
    return comparison.commits


def ensure_output_directory():
    """Create output directory if it doesn't exist"""
    output_dir = os.path.join(os.getcwd(), 'generated_docs')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    try:
        latest_ref, previous_ref = get_tags_or_commits()
        if not latest_ref or not previous_ref:
            print("Not enough history to generate release notes")
            return
        
        print("Fetching commits between references...")
        commits = get_commits_between_refs(latest_ref, previous_ref)
        
        print("Generating release notes...")
        release_notes = generate_release_notes(latest_ref, previous_ref, commits)
        
        output_dir = ensure_output_directory()
        output_file = os.path.join(
            output_dir, 
            f"release_notes_{datetime.now().strftime('%Y-%m-%d')}.md"
        )
        
        print(f"Writing release notes to: {output_file}")
        with open(output_file, 'w') as f:
            f.write(release_notes)
        
        print("✅ Release notes generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating release notes: {str(e)}")
        raise

if __name__ == "__main__":
    main()