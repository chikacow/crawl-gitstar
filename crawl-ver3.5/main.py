from token_manager import TokenManager, github_token_manager
from crawler.repo_crawler import crawl_repo

if __name__ == "__main__":
    GITHUB_TOKENS = github_token_manager()
    token_manager = TokenManager(GITHUB_TOKENS)
    crawl_repo(token_manager)
