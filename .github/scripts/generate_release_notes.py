import os
import requests
from datetime import datetime
from github import Github

def get_tags_or_commits():
    """Get latest tags or use commits if no/single tag exists"""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}")
    
    # Try to get tags
    tags = list(repo.get_tags())
    
    if len(tags) >= 2:
        print(f"Found multiple tags: {tags[0].name} and {tags[1].name}")
        return tags[0], tags[1]
    elif len(tags) == 1:
        print(f"Found single tag: {tags[0].name}")
        # Get commits before the tag
        commits = list(repo.get_commits(sha=tags[0].commit.sha + "^"))
        if commits:
            previous_commit = commits[min(10, len(commits)-1)]  # Get 10th commit or last available
            print(f"Using commit {previous_commit.sha[:7]} as previous reference")
            return tags[0], previous_commit
    
    # If no tags, use latest commits
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
    
    comparison = repo.compare(previous_ref.sha, latest_ref.sha)
    return comparison.commits

def generate_release_notes(latest_ref, previous_ref, commits):
    today = datetime.now().strftime("%Y-%m-%d")
    ref_type = "tag" if hasattr(latest_ref, "name") else "commit"
    
    notes = [
        f"# Release Notes ({today})",
        f"\nChanges between {'tags' if ref_type == 'tag' else 'commits'}:",
        f"- Latest: {latest_ref.name if ref_type == 'tag' else latest_ref.sha[:7]}",
        f"- Previous: {previous_ref.name if ref_type == 'tag' else previous_ref.sha[:7]}\n",
        "\n## Changes\n"
    ]
    
    # Rest of generate_release_notes remains the same...

def main():
    latest_ref, previous_ref = get_tags_or_commits()
    if not latest_ref or not previous_ref:
        print("Not enough history to generate release notes")
        return
    
    commits = get_commits_between_refs(latest_ref, previous_ref)
    release_notes = generate_release_notes(latest_ref, previous_ref, commits)
    
    output_dir = os.path.join(os.getcwd(), 'generated_docs')
    print(f"Creating output directory: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(
        output_dir, 
        f"release_notes_{datetime.now().strftime('%Y-%m-%d')}.md"
    )
    print(f"Writing release notes to: {output_file}")
    
    with open(output_file, 'w') as f:
        f.write(release_notes)
    
    print("Release notes generated successfully")