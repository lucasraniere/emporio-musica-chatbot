import sqlite3

from emporio.config import settings

def query(sql: str, params: tuple = ()) -> list[dict]:
    uri = f"file:{settings.sqlite_path}?mode=ro" # read only, we don't want the chat to modify the db
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params)]
