import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from db import get_connection, save_releases_bulk, save_commits_bulk  # dùng bulk insert

PER_PAGE = 100
session = requests.Session()

def fetch_github_json(url, token, params=None, retries=3):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    for attempt in range(retries):
        try:
            resp = session.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
                reset_time = int(resp.headers["X-RateLimit-Reset"])
                sleep_for = reset_time - int(time.time()) + 1
                print(f"[!] Rate limited. Sleeping for {sleep_for}s...")
                time.sleep(max(sleep_for, 1))
                continue
            if resp.ok:
                return resp.json()
            print(f"[!] GitHub API error: {resp.status_code} for URL: {url}")
        except requests.RequestException as e:
            print(f"[!] Request failed: {e} (attempt {attempt+1})")
            time.sleep(2 ** attempt)
    return None

def crawl_commits(owner, repo, base_tag, head_tag, release_id, token_manager):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_tag}...{head_tag}"
    page = 1
    all_commits = []

    while True:
        token = token_manager.get_token()
        data = fetch_github_json(url, token, {"page": page, "per_page": PER_PAGE})
        if not data or "commits" not in data:
            break
        commits = data["commits"]
        if not commits:
            break

        # Gom commit lại
        for c in commits:
            all_commits.append((c["sha"], c["commit"]["message"], release_id))

        if len(commits) < PER_PAGE:
            break
        page += 1

    # Ghi 1 lần duy nhất
    if all_commits:
        with get_connection() as (_, cursor):
            save_commits_bulk(cursor, all_commits)

def crawl_releases(owner, repo, repo_id, token_manager):
    print(f"▶ Crawling {owner}/{repo}")
    page = 1
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []

        while True:
            token = token_manager.get_token()
            releases = fetch_github_json(url, token, {"page": page, "per_page": PER_PAGE})
            if not releases:
                break

            releases.sort(key=lambda r: r.get("created_at", ""))

            to_save = []
            for r in releases:
                if "tag_name" in r and r["tag_name"]:
                    to_save.append((r["id"], r["tag_name"], r.get("body", ""), repo_id))
            if to_save:
                with get_connection() as (_, cursor):
                    save_releases_bulk(cursor, to_save)

            for i in reversed(range(len(releases))):
                if i == 0 or not releases[i].get("tag_name") or not releases[i-1].get("tag_name"):
                    continue
                release = releases[i]
                prev = releases[i - 1]
                futures.append(
                    executor.submit(
                        crawl_commits,
                        owner,
                        repo,
                        prev["tag_name"],
                        release["tag_name"],
                        release["id"],
                        token_manager
                    )
                )
            page += 1

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"[!] Error in commit crawl: {e}")
