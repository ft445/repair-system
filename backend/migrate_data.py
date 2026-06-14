"""
SQLite -> PostgreSQL 数据迁移脚本
用法: python migrate_data.py
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# 数据库连接
SQLITE_PATH = "repair_system.db"
PG_DSN = "host=localhost port=5432 dbname=repair_system user=postgres password=postgres"

# 迁移顺序（外键依赖决定顺序）
TABLE_ORDER = [
    "users",
    "organizations",
    "customers",
    "service_categories",
    "service_items",
    "technician_skills",
    "technician_wallets",
    "sms_logs",
    "withdraw_requests",
    "work_orders",
    "work_order_logs",
]


def safe_val(v):
    if v is None:
        return None
    return v


def truncate_all(pg_cur):
    tables = reversed(TABLE_ORDER)
    for t in tables:
        try:
            pg_cur.execute(f'TRUNCATE TABLE "{t}" CASCADE')
        except Exception:
            pass


def migrate():
    SIGN = "[OK]"
    print("=" * 50)
    print("SQLite -> PostgreSQL data migration")
    print("=" * 50)

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    pg_conn = psycopg2.connect(PG_DSN)
    pg_cur = pg_conn.cursor()

    truncate_all(pg_cur)
    pg_conn.commit()

    total_migrated = 0
    total_skipped = 0

    for table in TABLE_ORDER:
        try:
            sqlite_cur.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = sqlite_cur.fetchone()[0]
        except sqlite3.OperationalError:
            print(f"  [!] {table}: not found in SQLite, skipped")
            total_skipped += 1
            continue

        if count == 0:
            print(f"  [-] {table}: 0 rows, skipped")
            continue

        sqlite_cur.execute(f'PRAGMA table_info("{table}")')
        columns_info = sqlite_cur.fetchall()
        col_names = [c[1] for c in columns_info]

        sqlite_cur.execute(f'SELECT * FROM "{table}"')
        rows = sqlite_cur.fetchall()

        placeholders = ",".join(["%s"] * len(col_names))
        cols = ",".join(col_names)
        insert_sql = f'INSERT INTO "{table}" ({cols}) VALUES ({placeholders})'

        migrated = 0
        errors = 0
        for row in rows:
            values = [safe_val(row[c]) for c in col_names]
            try:
                pg_cur.execute(insert_sql, values)
                migrated += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  ERROR row {migrated+errors}: {e}")

        try:
            pg_cur.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM \"{table}\"))")
        except Exception:
            pass

        pg_conn.commit()
        total_migrated += migrated
        print(f"  {SIGN} {table}: {migrated} rows migrated" + (f" ({errors} errors)" if errors else ""))

    print()
    print("=" * 50)
    print(f"Done! Total: {total_migrated} rows, {total_skipped} tables skipped")
    print("=" * 50)

    pg_cur.close()
    pg_conn.close()
    sqlite_conn.close()


if __name__ == "__main__":
    migrate()
