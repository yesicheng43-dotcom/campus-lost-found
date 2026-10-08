from functools import wraps

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .db import (
    authenticate_user,
    create_item,
    create_user,
    get_item,
    get_user,
    list_owner_items,
    search_items,
    update_item_status,
)
from .validation import STATUS_OPTIONS, TYPE_LABELS, validate_item_form


bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            next_url = request.full_path.rstrip("?")
            return redirect(url_for("main.login", next=next_url))
        return view(*args, **kwargs)

    return wrapped_view


def current_username():
    return session.get("username")


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


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = authenticate_user(username, password)
        if user is None:
            flash("账号或密码不正确。", "error")
        else:
            session.clear()
            session["username"] = user["username"]
            flash(f"欢迎回来，{user['display_name']}！", "success")
            next_url = request.form.get("next", "")
            if next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("main.index"))
    return render_template("login.html", next=request.args.get("next", ""))


@bp.route("/register", methods=["GET", "POST"])
def register():
    data = {
        "username": "",
        "display_name": "",
        "student_id": "",
    }
    if request.method == "POST":
        data = {
            "username": request.form.get("username", "").strip(),
            "display_name": request.form.get("display_name", "").strip(),
            "student_id": request.form.get("student_id", "").strip(),
        }
        password = request.form.get("password", "")
        errors = []
        if len(data["username"]) < 3:
            errors.append("账号至少需要 3 个字符。")
        if len(password) < 6:
            errors.append("密码至少需要 6 个字符。")
        if not data["display_name"] or not data["student_id"]:
            errors.append("姓名和学号不能为空。")
        if not errors and create_user(
            data["username"], password, data["display_name"], data["student_id"]
        ):
            session.clear()
            session["username"] = data["username"]
            flash("注册成功。", "success")
            return redirect(url_for("main.my_posts"))
        if not errors:
            errors.append("账号已存在，请换一个账号。")
        for error in errors:
            flash(error, "error")
    return render_template("register.html", data=data)


@bp.post("/logout")
def logout():
    session.clear()
    flash("你已退出登录。", "success")
    return redirect(url_for("main.index"))


@bp.get("/publish")
@login_required
def publish_type():
    return render_template("publish_type.html")


@bp.get("/mine")
@login_required
def my_posts():
    user = get_user(current_username())
    return render_template("my_posts.html", items=list_owner_items(current_username()), user=user)


@bp.get("/items/<int:item_id>")
def item_detail(item_id):
    item = get_item(item_id)
    if item is None:
        abort(404)
    return render_template("detail.html", item=item)


@bp.route("/publish/<item_type>", methods=["GET", "POST"])
@login_required
def publish_item(item_type):
    if item_type not in TYPE_LABELS:
        abort(404)
    data = {field: "" for field in ("name", "category", "location", "event_time", "description", "contact")}
    errors = {}
    if request.method == "POST":
        data, errors = validate_item_form(request.form, item_type)
        if not errors:
            item_id = create_item(item_type, data, current_username())
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
@login_required
def change_item_status(item_id):
    status = request.form.get("status", "")
    if not update_item_status(item_id, status, current_username()):
        abort(400)
    flash("信息状态已更新。", "success")
    return redirect(url_for("main.my_posts"))
