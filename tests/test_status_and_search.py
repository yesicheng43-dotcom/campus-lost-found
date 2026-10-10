"""状态流转与筛选组合的补充测试。

现有 tests/test_app.py 覆盖了首页、搜索、发布校验、详情、登录和权限，
这里补上几处此前没有覆盖、但需求里明确要求的场景：

1. 发布后的初始状态是否符合状态机定义（寻物=寻找中，招领=待认领）；
2. 状态更新之后，列表页能否同步看到新状态；
3. 关键词与类型筛选能否组合生效；
4. 搜索无结果时是否给出空状态提示；
5. 未登录访问发布页是否被拦截；
6. 状态值非法时是否被拒绝。

这些用例的取值依据来自需求文档：状态选项只有
寻物「寻找中 / 已找到」和招领「待认领 / 已归还」两组，
其余取值都应当被服务端拒绝。
"""

import pytest

from app import create_app


def login(client, username="102402141", password="123456"):
    """登录辅助函数：默认使用种子数据里的学生账号。"""
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test_extra.sqlite3"),
        }
    )


# ---------- 1. 发布后的初始状态 ----------

def test_new_lost_item_starts_as_searching(app):
    """发布寻物后，状态应当是「寻找中」，而不是招领那一组状态。"""
    client = app.test_client()
    login(client)

    response = client.post(
        "/publish/lost",
        data={
            "name": "测试用折叠伞",
            "category": "生活用品",
            "location": "图书馆二楼",
            "event_time": "2026-10-10",
            "description": "黑色折叠伞，伞柄贴了一张蓝色贴纸。",
            "contact": "tester@example.com",
        },
        follow_redirects=True,
    )

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "寻找中" in body
    assert "待认领" not in body


def test_new_found_item_starts_as_pending_claim(app):
    """发布招领后，状态应当是「待认领」，而不是寻物那一组状态。"""
    client = app.test_client()
    login(client)

    response = client.post(
        "/publish/found",
        data={
            "name": "测试用保温杯",
            "category": "生活用品",
            "location": "第一食堂门口",
            "event_time": "2026-10-10",
            "description": "银灰色保温杯，杯盖有一道划痕。",
            "contact": "tester@example.com",
        },
        follow_redirects=True,
    )

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "待认领" in body
    assert "寻找中" not in body


# ---------- 2. 状态更新后列表同步 ----------

def test_status_update_is_visible_in_my_posts(app):
    """需求要求状态修改后其他页面同步更新，这里验证「我的」页面能看到新状态。"""
    client = app.test_client()
    login(client)

    client.post("/items/1/status", data={"status": "已找到"}, follow_redirects=True)
    response = client.get("/mine")

    assert response.status_code == 200
    assert "已找到" in response.get_data(as_text=True)


def test_status_update_is_visible_on_home_page(app):
    """首页卡片展示状态，更新后首页也应同步。"""
    client = app.test_client()
    login(client)

    client.post("/items/1/status", data={"status": "已找到"}, follow_redirects=True)
    response = client.get("/")

    assert response.status_code == 200
    assert "已找到" in response.get_data(as_text=True)


def test_invalid_status_value_is_rejected(app):
    """状态选项之外的取值应当被服务端拒绝，不能写进数据库。"""
    client = app.test_client()
    login(client)

    response = client.post("/items/1/status", data={"status": "随便写的状态"})

    assert response.status_code == 400


# ---------- 3. 关键词与类型筛选组合 ----------

def test_keyword_and_type_filter_work_together(app):
    """「黑色雨伞」是招领信息：筛招领时能看到，筛寻物时不应出现。"""
    client = app.test_client()

    found_body = client.get("/?keyword=雨伞&type=found").get_data(as_text=True)
    assert "黑色雨伞" in found_body

    lost_body = client.get("/?keyword=雨伞&type=lost").get_data(as_text=True)
    assert "黑色雨伞" not in lost_body


def test_search_matches_location_field(app):
    """关键词也要能命中地点，例如输入「西区」应搜到西区教学楼的信息。"""
    client = app.test_client()

    body = client.get("/?keyword=西区").get_data(as_text=True)

    assert "西区教学楼" in body


# ---------- 4. 搜索无结果的空状态 ----------

def test_search_without_match_shows_empty_state(app):
    """搜不到东西时要有明确提示，不能只是白屏。"""
    client = app.test_client()

    response = client.get("/?keyword=完全不存在的物品名称")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "没有找到相关信息" in body
    assert "校园卡" not in body


# ---------- 5. 未登录的访问控制 ----------

def test_publish_page_requires_login(app):
    """未登录访问发布页应跳转登录，并带上回跳地址。"""
    client = app.test_client()

    response = client.get("/publish")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_publish_form_requires_login(app):
    """未登录直接访问发布表单同样要被拦住。"""
    client = app.test_client()

    response = client.get("/publish/lost")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
