"""
Example file with intentional issues — used to demonstrate the AI Code Reviewer.
DO NOT use this code in production.
"""

import sqlite3
import subprocess
import hashlib


# Security: hardcoded credentials
DB_PASSWORD = "admin123"
SECRET_KEY = "my-super-secret-key-12345"


def get_user(username: str):
    """Security: SQL injection vulnerability."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: f-string directly in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()


def hash_password(password: str) -> str:
    """Security: weak hashing algorithm."""
    # BAD: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


def process_file(filename: str):
    """Security: shell injection via subprocess."""
    # BAD: shell=True with user-controlled input
    result = subprocess.run(f"cat {filename}", shell=True, capture_output=True)
    return result.stdout.decode()


def calculate_sum(items: list) -> int:
    """Performance: inefficient loop."""
    total = 0
    result_str = ""
    for i in range(len(items)):
        total = total + items[i]
        result_str = result_str + str(items[i]) + ","
    return total


def load_all_users():
    """Performance: loads entire table into memory."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # BAD: no LIMIT, could load millions of rows
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


def divide(a, b):
    """Bug: no zero-division guard."""
    return a / b


def find_item(items: list, target):
    """Bug: off-by-one error."""
    for i in range(len(items) + 1):
        if items[i] == target:
            return i
    return -1
