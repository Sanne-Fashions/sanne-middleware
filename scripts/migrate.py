"""Apply SQL migrations in order. Usage: DATABASE_URL=... python scripts/migrate.py"""

import os
import pathlib

import psycopg

MIGRATIONS = pathlib.Path(__file__).resolve().parent.parent / "db" / "migrations"


def main() -> None:
    url = os.environ["DATABASE_URL"]
    with psycopg.connect(url) as conn:
        for path in sorted(MIGRATIONS.glob("*.sql")):
            print(f"applying {path.name}")
            conn.execute(path.read_text())
        conn.commit()
    print("done")


if __name__ == "__main__":
    main()
