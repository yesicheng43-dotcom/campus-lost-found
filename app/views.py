from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

from .db import create_item, get_item, list_owner_items, search_items, update_item_status
from .validation import STATUS_OPTIONS, TYPE_LABELS, validate_item_form


bp = Blueprint("main", __name__)
DEMO_OWNER = "demo-user"


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
    return render_template("publish_type.html")


@bp.get("/mine")
def my_posts():
    return render_template("my_posts.html", items=list_owner_items(DEMO_OWNER))


@bp.get("/items/<int:item_id>")
def item_detail(item_id):
    item = get_item(item_id)
    if item is None:
        abort(404)
    return render_template("detail.html", item=item)


@bp.route("/publish/<item_type>", methods=["GET", "POST"])
def publish_item(item_type):
    if item_type not in TYPE_LABELS:
        abort(404)
    data = {field: "" for field in ("name", "category", "location", "event_time", "description", "contact")}
    errors = {}
    if request.method == "POST":
        data, errors = validate_item_form(request.form, item_type)
        if not errors:
            item_id = create_item(item_type, data, DEMO_OWNER)
            flash("信息发布成功，可以在“我的”中查看。", "success")
            return redirect(url_for("main.item_detail", item_id=item_id))
        flash("请补全表单后再提交。", "error")
    return render_template(
        "publish_form.html",
        item_type=item_type,
        type_label=TYPE_LABELS[item_type],
        data=data,
        errors=errors,
    ), (400 if errors else 200)


@bp.post("/items/<int:item_id>/status")
def change_item_status(item_id):
    status = request.form.get("status", "")
    if not update_item_status(item_id, status, DEMO_OWNER):
        abort(400)
    flash("信息状态已更新。", "success")
    return redirect(url_for("main.my_posts"))
