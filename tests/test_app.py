from app import create_app
import pytest


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

    response = client.post(
        "/items/1/status",
        data={"status": "已找到"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "已找到" in response.get_data(as_text=True)
