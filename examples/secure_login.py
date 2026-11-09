"""Synthetic example using parameterization."""
import sqlite3


def secure_lookup(connection: sqlite3.Connection, username: str):
    return connection.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
