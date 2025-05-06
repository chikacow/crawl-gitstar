import time
import requests
from db import cnxpool, save_release_to_db
from concurrent.futures import ThreadPoolExecutor
from crawler.commit_crawler import crawl_commit_between_tags

def crawl_release(owner, repo, repo_id, token_manager):
    print(f"▶ Crawling releases for {owner}/{repo}")
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    page = 1

    conn = cnxpool.get_connection()
    cursor = conn.cursor()

    try:
        while True:
            token = token_manager.get_token()
            headers = {"Authorization": f"token {token}"}
            params = {"page": page, "per_page": 100}
            resp = requests.get(url, headers=headers, params=params)

            if resp.status_code != 200:
                print(f"✘ Failed to fetch releases for {owner}/{repo}")
                break

            releases = resp.json()
            if not releases:
                break

            releases.sort(key=lambda r: r.get("created_at", ""))
            with ThreadPoolExecutor(max_workers=8) as executor:
                for i in range(len(releases) - 1, -1, -1):
                    release = releases[i]
                    if i == 0:
                        continue
                    prev_release = releases[i - 1]

                    release_id = release.get("id")
                    tag = release.get("tag_name")
                    body = release.get("body", "")
                    prev_tag = prev_release.get("tag_name")

                    save_release_to_db(cursor, release_id, tag, body, repo_id)
                    executor.submit(crawl_commit_between_tags, owner, repo, prev_tag, tag, release_id, token_manager)

            page += 1
            time.sleep(1)
    finally:
        cursor.close()
        conn.close()
