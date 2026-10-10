from app import create_app
import pytest


def login(client):
    return client.post(
        "/login",
        data={"username": "102402141", "password": "123456"},
        follow_redirects=True,
    )


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.sqlite3"),
        }
    )


def test_health_endpoint(app):
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_home_page_is_available(app):
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "校园失物招领" in response.get_data(as_text=True)
    assert "校园卡" in response.get_data(as_text=True)


def test_keyword_search_filters_items(app):
    client = app.test_client()

    response = client.get("/?keyword=雨伞")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "黑色雨伞" in body
    assert "校园卡" not in body


def test_publish_lost_item_and_redirect_to_detail(app):
    client = app.test_client()
    login(client)

    response = client.post(
        "/publish/lost",
        data={
            "name": "耳机",
            "category": "电子产品",
            "location": "图书馆一楼",
            "event_time": "2026-10-08",
            "description": "白色无线耳机，收纳盒上有贴纸。",
            "contact": "campus-123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "耳机" in response.get_data(as_text=True)
    assert "图书馆一楼" in response.get_data(as_text=True)


def test_publish_requires_required_fields(app):
    client = app.test_client()
    login(client)

    response = client.post("/publish/found", data={})

    assert response.status_code == 400
    assert "此项不能为空" in response.get_data(as_text=True)


def test_detail_page_shows_seed_item(app):
    client = app.test_client()

    response = client.get("/items/1")

    assert response.status_code == 200
    assert "校园卡" in response.get_data(as_text=True)
    assert "东区教学楼 306" in response.get_data(as_text=True)


def test_owner_can_update_item_status(app):
    client = app.test_client()
    login(client)

    response = client.post(
        "/items/1/status",
        data={"status": "已找到"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "已找到" in response.get_data(as_text=True)


def test_missing_item_has_friendly_not_found_page(app):
    client = app.test_client()

    response = client.get("/items/9999")

    assert response.status_code == 404
    assert "找不到这条信息" in response.get_data(as_text=True)


def test_protected_pages_require_login(app):
    client = app.test_client()

    response = client.get("/mine")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_student_can_login_and_view_personal_page(app):
    client = app.test_client()

    login(client)
    response = client.get("/mine")

    assert response.status_code == 200
    assert "叶思铖" in response.get_data(as_text=True)
    assert "102402141" in response.get_data(as_text=True)


def test_invalid_login_shows_error(app):
    client = app.test_client()

    response = client.post(
        "/login",
        data={"username": "102402141", "password": "wrong-password"},
    )

    assert response.status_code == 200
    assert "账号或密码不正确" in response.get_data(as_text=True)


def test_login_page_does_not_expose_demo_credentials_or_register_link(app):
    client = app.test_client()

    response = client.get("/login")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "demo-user" not in body
    assert "123456" not in body
    assert "立即注册" not in body


def test_user_can_update_own_contact_information(app):
    client = app.test_client()
    login(client)

    response = client.post(
        "/profile/edit",
        data={"email": "new141@example.com", "phone": "13900000001"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "new141@example.com" in body
    assert "13900000001" in body


def test_normal_user_cannot_update_another_users_item(app):
    client = app.test_client()
    login(client)

    response = client.post("/items/4/status", data={"status": "已找到"})

    assert response.status_code == 400


def test_admin_can_update_any_users_item(app):
    client = app.test_client()
    client.post(
        "/login",
        data={"username": "admin", "password": "123456"},
    )

    response = client.post(
        "/items/4/status",
        data={"status": "已找到"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "白色耳机" in response.get_data(as_text=True)
    assert "已找到" in response.get_data(as_text=True)


def test_register_creates_account_and_logs_in(app):
    client = app.test_client()

    response = client.post(
        "/register",
        data={
            "username": "new-user",
            "password": "abcdef",
            "display_name": "新同学",
            "student_id": "20260001",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "新同学" in response.get_data(as_text=True)
    assert "20260001" in response.get_data(as_text=True)
