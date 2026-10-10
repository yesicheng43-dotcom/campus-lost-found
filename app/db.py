import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import check_password_hash, generate_password_hash

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
    database.execute(
        """
        INSERT INTO users
          (username, password_hash, display_name, student_id, faculty, email, phone, role, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "102402141",
            generate_password_hash("123456"),
            "叶思铖",
            "102402141",
            "计算机与大数据学院",
            "102402141@example.com",
            "13800000001",
            "user",
            "/static/assets/avatar.png",
        ),
    )
    database.execute(
        """
        INSERT INTO users
          (username, password_hash, display_name, student_id, faculty, email, phone, role, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "102402142",
            generate_password_hash("123456"),
            "叶腾骏",
            "102402142",
            "计算机与大数据学院",
            "102402142@example.com",
            "13800000002",
            "user",
            "/static/assets/avatar-102402142.png",
        ),
    )
    database.execute(
        """
        INSERT INTO users
          (username, password_hash, display_name, student_id, faculty, email, phone, role, avatar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "admin",
            generate_password_hash("123456"),
            "系统管理员",
            "",
            "",
            "",
            "",
            "admin",
            "",
        ),
    )
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
                "/static/assets/item-campus-card.png",
                "102402141@example.com",
                "寻找中",
                "102402141",
            ),
            (
                "found",
                "黑色雨伞",
                "生活用品",
                "西区教学楼 201",
                "2026-09-21",
                "在教室后排捡到一把黑色长柄雨伞。",
                "/static/assets/item-umbrella.png",
                "102402141@example.com",
                "待认领",
                "102402141",
            ),
            (
                "lost",
                "篮球",
                "运动用品",
                "东区体育馆",
                "2026-09-20",
                "橙色篮球，表面有一处明显的黑色记号。",
                "/static/assets/item-basketball.png",
                "102402141@example.com",
                "寻找中",
                "102402141",
            ),
            (
                "lost",
                "白色耳机",
                "电子产品",
                "西区教学楼 306",
                "2026-09-22",
                "白色无线耳机，收纳盒上有蓝色贴纸。",
                "/static/assets/item-earbuds.png",
                "102402142@example.com",
                "寻找中",
                "102402142",
            ),
            (
                "found",
                "水杯",
                "生活用品",
                "图书馆一楼",
                "2026-09-23",
                "透明水杯，杯身有蓝色挂绳。",
                "/static/assets/item-bottle.png",
                "102402142@example.com",
                "待认领",
                "102402142",
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
        if (
            not database.exists()
            or not _has_table("users")
            or not _has_column("users", "role")
            or not _has_column("users", "faculty")
            or not _has_column("users", "email")
            or not _has_column("users", "phone")
        ):
            init_db()


def _has_table(table_name):
    return (
        get_db()
        .execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        )
        .fetchone()
        is not None
    )


def _has_column(table_name, column_name):
    columns = get_db().execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(column[1] == column_name for column in columns)


def search_items(keyword="", item_type="all", status="all", category="all"):
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
    if category and category != "all":
        clauses.append("category = ?")
        parameters.append(category)

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


def list_categories():
    """列出当前已出现的物品类别，供首页筛选按钮使用。"""
    rows = get_db().execute(
        "SELECT DISTINCT category FROM items WHERE category <> '' ORDER BY category"
    ).fetchall()
    return [row["category"] for row in rows]


def list_all_items():
    return get_db().execute(
        "SELECT * FROM items ORDER BY created_at DESC, id DESC"
    ).fetchall()


def update_item_status(item_id, status, owner, can_manage_all=False):
    item = get_item(item_id)
    if item is None or (not can_manage_all and item["owner"] != owner):
        return False
    if status not in STATUS_OPTIONS[item["type"]]:
        return False
    database = get_db()
    database.execute("UPDATE items SET status = ? WHERE id = ?", (status, item_id))
    database.commit()
    return True


def get_user(username):
    return get_db().execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def authenticate_user(username, password):
    user = get_user(username)
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return user


def create_user(
    username,
    password,
    display_name,
    student_id,
    faculty="计算机与大数据学院",
    email="",
    phone="",
):
    database = get_db()
    try:
        cursor = database.execute(
            """
            INSERT INTO users
              (username, password_hash, display_name, student_id, faculty, email, phone, role, avatar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash(password),
                display_name,
                student_id,
                faculty,
                email,
                phone,
                "user",
                "/static/assets/avatar.png",
            ),
        )
        database.commit()
    except sqlite3.IntegrityError:
        return None
    return cursor.lastrowid


def update_user_contact(username, email, phone):
    database = get_db()
    database.execute(
        "UPDATE users SET email = ?, phone = ? WHERE username = ?",
        (email, phone, username),
    )
    database.commit()
