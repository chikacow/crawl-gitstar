import os
import sys
from dotenv import load_dotenv
from token_manager import TokenManager
from github_crawler import crawl_releases
from db import get_connection
from concurrent.futures import ThreadPoolExecutor

def get_tokens():
    load_dotenv()
    i, tokens = 1, []
    while token := os.getenv(f"GITHUB_TOKEN_{i}"):
        tokens.append(token.strip())
        i += 1
    return tokens

def crawl_all_repos(token_manager, max_workers=8):
    with get_connection() as (_, cursor):
        cursor.execute("SELECT user, name, id FROM repo WHERE id > 0")
        repos = cursor.fetchall()

    print(f"▶ Found {len(repos)} repositories.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for user, name, repo_id in repos:
            #print(f"⏳ Submitting: {user}/{name}")
            executor.submit(crawl_releases, user, name, repo_id, token_manager)

if __name__ == "__main__":
    tokens = get_tokens()
    if not tokens:
        sys.exit("? where the fuk is pat in .env")

    tm = TokenManager(tokens)
    crawl_all_repos(tm, 32)
