"""PostgreSQL access. Only this service talks to the database; n8n never connects to it."""

import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(self, url: str):
        self._url = url

    def _connect(self):
        return psycopg.connect(self._url, row_factory=dict_row)

    def fetch_chart(self, product_id: str) -> list[dict]:
        with self._connect() as conn:
            return conn.execute(
                """SELECT size, measure, target_cm, tolerance_cm
                   FROM size_charts
                   WHERE product_id = %s
                   ORDER BY size, measure""",
                (product_id,),
            ).fetchall()

    def ping(self) -> bool:
        with self._connect() as conn:
            conn.execute("SELECT 1")
        return True
