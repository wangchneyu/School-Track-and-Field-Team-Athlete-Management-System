# Alembic Setup

1. 依赖已在 `requirements.txt`，环境初始化完毕（`alembic.ini` + `alembic/env.py` 已配置）。
2. 连接串取自 `.env`：`DB_ENGINE/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME`（默认 MySQL 8，端口 3307）。
3. 常用命令：
   - 生成迁移：`alembic revision --autogenerate -m "message"`
   - 执行迁移：`alembic upgrade head`
   - 回滚一步：`alembic downgrade -1`
4. 目标元数据位于 `app.db.base.Base`，模型通过 `import app.models` 自动注册。
