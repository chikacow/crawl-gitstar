from concurrent.futures import ThreadPoolExecutor
from db import cnxpool
from crawler.release_crawler import crawl_release

def crawl_repo(token_manager):
    conn = cnxpool.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user, name, id FROM repo WHERE id > 0")
    repos = cursor.fetchall()

    cursor.close()
    conn.close()

    print(f"Found {len(repos)} repos to crawl.")
    futures = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        for user, name, repo_id in repos:
            futures.append(executor.submit(crawl_release, user, name, repo_id, token_manager))
        for future in futures:
            future.result()
    print("✅ All repos processed.")
