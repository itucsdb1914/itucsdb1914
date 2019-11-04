import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS USER(
        USER_ID SERIAL PRIMARY KEY,
        NAME VARCHAR(50) NOT NULL,
        USERNAME VARCHAR(30) UNIQUE NOT NULL,
        PASSWORD VARCHAR(50) NOT NULL,
        EMAIL VARCHAR(100) UNIQUE NOT NULL,
    )""",
    """CREATE TABLE IF NOT EXISTS EVENTS(
        EVENT_ID SERIAL PRIMARY KEY,
        TITLE VARCHAR(50) NOT NULL
    )"""
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
