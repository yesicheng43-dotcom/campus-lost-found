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
