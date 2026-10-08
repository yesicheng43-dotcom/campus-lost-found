import sqlite3
from pathlib import Path

import click
from flask import current_app, g

from .validation import STATUS_OPTIONS


def get_db():
    if "db" not in g:
        database = Path(current_app.config["DATABASE"])
        database.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    schema_path = Path(current_app.root_path).joinpath("schema.sql")
    database.executescript(schema_path.read_text(encoding="utf-8"))
    database.executemany(
        """
        INSERT INTO items
          (type, name, category, location, event_time, description, image,
           contact, status, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "lost",
                "校园卡",
                "证件",
                "东区教学楼 306",
                "2026-09-22",
                "蓝色校园卡，卡套上有白色挂绳。",
                "",
                "campus-card@example.com",
                "寻找中",
                "demo-user",
            ),
            (
                "found",
                "黑色雨伞",
                "生活用品",
                "西区教学楼 201",
                "2026-09-21",
                "在教室后排捡到一把黑色长柄雨伞。",
                "",
                "umbrella@example.com",
                "待认领",
                "demo-user",
            ),
            (
                "lost",
                "篮球",
                "运动用品",
                "东区体育馆",
                "2026-09-20",
                "橙色篮球，表面有一处明显的黑色记号。",
                "",
                "basketball@example.com",
                "寻找中",
                "demo-user",
            ),
        ],
    )
    database.commit()


@click.command("init-db")
def init_db_command():
    """Clear and initialize the local database with demo data."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    with app.app_context():
        database = Path(app.config["DATABASE"])
        if not database.exists():
            init_db()


def search_items(keyword="", item_type="all", status="all"):
    database = get_db()
    clauses = []
    parameters = []

    keyword = keyword.strip()
    if keyword:
        clauses.append("(name LIKE ? OR location LIKE ? OR description LIKE ?)")
        value = f"%{keyword}%"
        parameters.extend([value, value, value])
    if item_type in {"lost", "found"}:
        clauses.append("type = ?")
        parameters.append(item_type)
    if status and status != "all":
        clauses.append("status = ?")
        parameters.append(status)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return database.execute(
        f"SELECT * FROM items {where} ORDER BY created_at DESC, id DESC",
        parameters,
    ).fetchall()


def get_item(item_id):
    return get_db().execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()


def create_item(item_type, data, owner):
    status = STATUS_OPTIONS[item_type][0]
    database = get_db()
    cursor = database.execute(
        """
        INSERT INTO items
          (type, name, category, location, event_time, description, image,
           contact, status, owner)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_type,
            data["name"],
            data["category"],
            data["location"],
            data["event_time"],
            data["description"],
            data.get("image", ""),
            data["contact"],
            status,
            owner,
        ),
    )
    database.commit()
    return cursor.lastrowid


def list_owner_items(owner):
    return get_db().execute(
        "SELECT * FROM items WHERE owner = ? ORDER BY created_at DESC, id DESC",
        (owner,),
    ).fetchall()


def update_item_status(item_id, status, owner):
    item = get_item(item_id)
    if item is None or item["owner"] != owner:
        return False
    if status not in STATUS_OPTIONS[item["type"]]:
        return False
    database = get_db()
    database.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
    database.commit()
    return True
