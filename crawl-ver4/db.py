import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import time

POOL_SIZE = 32

# Cấu hình kết nối
dbconfig = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "mysqL2004@",
    "database": "crawl",
    "autocommit": True,
    "use_unicode": True,
    "charset": "utf8mb4",
}

# Tạo connection pool
pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=POOL_SIZE, **dbconfig)

# Context manager để lấy kết nối và cursor an toàn
@contextmanager
def get_connection():
    conn = pool.get_connection()
    cursor = conn.cursor(buffered=True)
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()


def save_releases_bulk(cursor, releases):
    """
    releases: List of tuples (id, version, content, repo_id)
    """
    query = """
        INSERT IGNORE INTO `release` (id, version, content, repoID)
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(query, releases)
        time.sleep(0.5) 
    except mysql.connector.Error as e:
        
        print(f"✘ Error saving commit {e}")
        


def save_commits_bulk(cursor, commits):
    """
    commits: List of tuples (hash, message, release_id)
    """
    query = """
        INSERT IGNORE INTO `commit` (hash, message, releaseID)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.executemany(query, commits)
        
    except mysql.connector.Error as e:
        
        print(f"✘ Error saving commit {e}")


def save_all_data(releases, commits):
    with get_connection() as (conn, cursor):
        if releases:
            save_releases_bulk(cursor, releases)
        if commits:
            save_commits_bulk(cursor, commits)
        conn.commit()  # chỉ gọi 1 lần

