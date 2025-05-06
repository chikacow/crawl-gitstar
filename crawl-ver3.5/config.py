import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "mysqL2004@",
    "database": "crawl",
    "autocommit": True,
    "use_unicode": True,
    "charset": "utf8mb4",
}

PER_PAGE = 100
