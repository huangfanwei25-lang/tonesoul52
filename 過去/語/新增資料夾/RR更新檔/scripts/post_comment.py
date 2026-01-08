import os
import requests
import sys

def post_comment(repo, pr_number, comment, token):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    data = {"body": comment}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        print(f"Failed to post comment: {response.status_code} - {response.text}")
        sys.exit(1)
    print("Comment posted successfully.")

if __name__ == "__main__":
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")
    token = os.environ.get("GITHUB_TOKEN")
    comment_file = sys.argv[1] if len(sys.argv) > 1 else "artifacts/report.md"
    comment = open(comment_file).read()
    post_comment(repo, pr_number, comment, token)