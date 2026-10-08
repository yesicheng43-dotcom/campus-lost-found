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

第一阶段 Flask 基础骨架已完成，包含首页占位页面和健康检查接口。业务数据和发布流程将在后续功能分支中加入。

