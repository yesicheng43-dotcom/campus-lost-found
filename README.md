# 校园失物招领

2026 秋软件工程结对作业：校园失物招领程序实现。

## 项目说明

本项目根据 Figma 原型实现校园失物招领 Web 应用，覆盖浏览、搜索、发布、详情和个人发布管理等核心流程。

## 开发约定

开始修改代码前请阅读 [PROJECT_RULES.md](PROJECT_RULES.md)。其中记录了技术路线、功能边界、分支协作、提交规范、测试要求和 AI 协作规则。

## 本地运行

项目使用 Python 3.10 及以上版本。Windows PowerShell 中可以执行：

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

启动后访问 `http://127.0.0.1:5000/`。如果 PowerShell 不允许激活虚拟环境，可以直接使用 `.venv\Scripts\python.exe` 执行命令。

运行测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 当前状态

当前功能分支已经完成第一版核心流程：

- 首页列表、关键词搜索和寻物/招领类型筛选；
- 基础账号注册、登录和退出，发布与个人管理需要登录；
- 寻物和招领发布表单，包含必填项校验；
- 信息详情和联系方式复制；
- “我的发布”列表及信息状态更新；
- 原型中的校园背景、物品图、发布卡片和头像素材已放入 `static/assets`；
- SQLite 演示数据、本地持久化和友好的错误页面。

提交前请运行 `.\.venv\Scripts\python.exe -m pytest -q`，并在浏览器中依次检查首页、发布、详情和“我的”页面。

登录账号由项目成员或管理员单独分配，登录页不会展示账号、密码或演示凭据。注册代码和路由暂时保留，但页面不提供注册入口。

