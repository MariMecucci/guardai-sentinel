"""SYNTHETIC training example; NEVER use in production."""
import sqlite3


def vulnerable_lookup(connection: sqlite3.Connection, username: str):
    query = f"SELECT id FROM users WHERE username = '{username}'"
    return connection.execute(query).fetchone()
