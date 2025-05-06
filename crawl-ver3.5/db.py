from mysql.connector import pooling
from config import DB_CONFIG

# Connection pool
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=32, **DB_CONFIG)

# Queries
insert_release_query = """
INSERT IGNORE INTO `release` (id, version, content, repoID)
VALUES (%s, %s, %s, %s)
"""

insert_commit_query = """
INSERT IGNORE INTO `commit` (hash, message, releaseID)
VALUES (%s, %s, %s)
"""

def save_release_to_db(cursor, release_id, release_tag, body, repo_id):
    from time import sleep
    try:
        cursor.execute(insert_release_query, (release_id, release_tag, body, repo_id))
        print(f"✔ Saved release {release_tag}")
        sleep(0.5)
    except Exception as e:
        print(f"✘ Error saving release {release_tag}: {e}")

def save_commit_to_db(cursor, sha, commit_message, release_id):
    try:
        cursor.execute(insert_commit_query, (sha, commit_message, release_id))
    except Exception as e:
        print(f"✘ Error saving commit {sha}: {e}")
