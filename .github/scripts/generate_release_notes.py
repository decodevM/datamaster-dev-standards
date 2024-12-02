import os
import requests
from datetime import datetime
from github import Github

def get_tags():
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}")
    
    # Get all tags sorted by creation date
    tags = sorted(repo.get_tags(), key=lambda t: t.commit.commit.author.date, reverse=True)
    
    if len(tags) < 2:
        return None, None
        
    return tags[0], tags[1]  # Latest and previous tags

def get_commits_between_tags(latest_tag, previous_tag):
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(f"{os.getenv('REPO_OWNER')}/{os.getenv('REPO_NAME')}")
    
    # Get commits between tags
    comparison = repo.compare(previous_tag.commit.sha, latest_tag.commit.sha)
    return comparison.commits

def generate_release_notes(latest_tag, previous_tag, commits):
    today = datetime.now().strftime("%Y-%m-%d")
    notes = [
        f"# Release Notes ({today})",
        f"\nChanges between {previous_tag.name} and {latest_tag.name}\n",
        "\n## Changes\n"
    ]
    
    # Group commits by type
    grouped_commits = {}
    for commit in commits:
        message = commit.commit.message.split('\n')[0]  # Get first line
        
        # Try to parse conventional commits
        if ':' in message:
            type = message.split(':')[0].split('(')[0].strip()
            if type not in grouped_commits:
                grouped_commits[type] = []
            grouped_commits[type].append(message)
        else:
            if 'other' not in grouped_commits:
                grouped_commits['other'] = []
            grouped_commits['other'].append(message)
    
    # Generate formatted notes
    for type, messages in grouped_commits.items():
        notes.append(f"### {type.capitalize()}")
        for msg in messages:
            notes.append(f"- {msg}")
        notes.append("")
    
    return '\n'.join(notes)

def main():
    latest_tag, previous_tag = get_tags()
    if not latest_tag or not previous_tag:
        print("Not enough tags found")
        return
    
    commits = get_commits_between_tags(latest_tag, previous_tag)
    release_notes = generate_release_notes(latest_tag, previous_tag, commits)
    
    # Save release notes
    os.makedirs('generated_docs', exist_ok=True)
    with open(f'generated_docs/release_notes_{datetime.now().strftime("%Y-%m-%d")}.md', 'w') as f:
        f.write(release_notes)

if __name__ == "__main__":
    main()