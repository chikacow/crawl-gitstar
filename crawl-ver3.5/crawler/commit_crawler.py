import requests
from db import cnxpool, save_commit_to_db

def crawl_commit_between_tags(owner, repo, base_tag, head_tag, release_id, token_manager):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_tag}...{head_tag}"
    page = 1

    while True:
        token = token_manager.get_token()
        headers = {"Authorization": f"token {token}"}
        params = {"page": page, "per_page": 100}
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code == 200:
            data = resp.json()
            commits = data.get("commits", [])
            if not commits:
                break

            print(f"✔ Found {len(commits)} commits between {base_tag} → {head_tag}")
            conn = cnxpool.get_connection()
            cursor = conn.cursor()
            try:
                for commit in commits:
                    sha = commit["sha"]
                    msg = commit["commit"]["message"]
                    save_commit_to_db(cursor, sha, msg, release_id)
            finally:
                cursor.close()
                conn.close()

            if len(commits) < 100:
                break
            page += 1
        else:
            print(f"✘ Compare failed for {base_tag}...{head_tag}")
            break
