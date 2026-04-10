# 校级田径组织考勤与成绩平台
<img width="2560" height="1398" alt="image" src="https://github.com/user-attachments/assets/88d5a39e-ac9e-443f-915d-b3bf8f6b576a" />

基于 **FastAPI + Postgre + 原生前端** 的校级田径队管理系统，可记录考勤、成绩、排行榜，并提供运动员 / 管理员双面板界面。

## 运行环境
- Python 3.11+
- pip / virtualenv

## 快速上手
```bash
# 1. 克隆或下载本项目后，进入目录
# 2. 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt

# 3. 拷贝环境变量样例，可按需修改数据库或 CORS 设置
copy .env.example .env          # Windows
# 若使用 Git Bash: cp .env.example .env

# 4. 初始化数据库并写入示例数据（管理员/运动员账号、赛事、考勤、成绩等）
python scripts/seed_data.py

# 5. 启动服务（默认 http://127.0.0.1:8000）
uvicorn main:app --reload
```

> 如需使用其它端口，追加 `--port 9000` 等参数。首次启动会自动创建 `athletics.db` 文件。

## 体验账号
| 角色 | 账号 | 密码 | 说明 |
| --- | --- | --- | --- |
| 管理员 | `admin` | `Admin123!` | 可管理赛事/统计/考勤等 |
| 运动员 | `2023001` | `123456` | 短跑组，示例考勤/成绩 |
| 运动员 | `2023002` | `123456` | 中长跑组，示例考勤/成绩 |

> 运动员首次登录后建议立即在个人面板中修改密码。管理员也可在后台页面修改自身密码。

## 访问路径
- `http://127.0.0.1:8000/` 自动跳转到登录页（`/static/index.html`）
- 登录成功后根据角色跳转：
  - 管理员：`/static/admin.html`
  - 运动员：`/static/athlete.html`

## 功能概览
- **登录 & 授权**：使用 OAuth2 密码模式，返回 JWT。运动员账号即学号，初始密码 `123456`。
- **赛事倒计时**：管理员可在后台配置赛事名称 / 时间 / 地点，前台自动显示倒计时。
- **考勤/成绩/评分**：管理员端展示统计，运动员端可查看个人历史。
- **统计面板**：后台提供出勤率表格、项目人数占比，可直接用于可视化。

## 开发辅助
- 配置文件：`app/core/config.py`，通过 `.env` 注入。
- 数据模型：`app/models/`
- API 路由：`app/api/routes/`
- 前端静态文件：`frontend/`
- 示例数据脚本：`scripts/seed_data.py`

## 常见问题
1. **登录失败 / 提示重新登录**：请在浏览器控制台清空 `localStorage`，重新登录。
2. **端口冲突**：修改 `uvicorn main:app --reload --port 9001`。
3. **需要重置数据库**：删除 `athletics.db` 后重新运行 `python scripts/seed_data.py`。

## Docker 运行
```bash
# 1. 构建镜像（首次）
docker compose build

# 2. （可选）在容器环境中写入示例数据
docker compose run --rm app python scripts/seed_data.py

# 3. 启动服务
docker compose up
# 或后台运行： docker compose up -d
```
