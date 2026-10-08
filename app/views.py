from flask import Blueprint, jsonify, render_template, request

from .db import search_items


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    keyword = request.args.get("keyword", "")
    item_type = request.args.get("type", "all")
    status = request.args.get("status", "all")
    items = search_items(keyword, item_type, status)
    return render_template(
        "index.html",
        items=items,
        keyword=keyword,
        selected_type=item_type,
        selected_status=status,
    )


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/publish")
def publish_type():
    return render_template("coming_soon.html", title="发布信息")


@bp.get("/mine")
def my_posts():
    return render_template("coming_soon.html", title="我的发布")


@bp.get("/items/<int:item_id>")
def item_detail(item_id):
    return render_template("coming_soon.html", title=f"信息详情 #{item_id}")
