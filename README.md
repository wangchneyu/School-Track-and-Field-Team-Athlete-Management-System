# 校田径队管理系统

基于 **FastAPI + Vue 3 + PostgreSQL** 的校级田径队队员管理系统，前后端分离架构，现代化 UI 设计，完美适配 PC 端和移动端。

## 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                     前端 (Vue 3 + Vite + TS)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  登录页面   │  │  管理员后台  │  │ 运动员端  │  │  扫码签到   │ │
│  │  粒子动画   │  │  侧栏分区   │  │ 底栏导航  │  │  Token输入  │ │
│  └────────────┘  └─────────────┘  └──────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                          │ RESTful API (JSON)
┌──────────────────────────────────────────────────────────────────┐
│                     API 层 (FastAPI)                               │
│  • JWT 认证   • CORS 跨域   • Swagger 自动文档   • 角色鉴权       │
└──────────────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────────────┐
│                     业务逻辑层 (Services)                          │
│  运动员管理 │ 训练管理 │ 考勤管理 │ 成绩管理 │ 评分排名 │ 训练内容  │
└──────────────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────────────┐
│                     数据层 (SQLAlchemy + PostgreSQL)               │
│  User │ Athlete │ Session │ Attendance │ Score │ Event │ Rating   │
└──────────────────────────────────────────────────────────────────┘
```

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + TypeScript | 组合式 API，类型安全 |
| 构建工具 | Vite 6 | 极速开发体验 |
| CSS 框架 | Tailwind CSS 3 | 原子化样式 + 自定义设计系统 |
| 状态管理 | Pinia | Vue 官方状态管理 |
| 路由 | Vue Router 4 | SPA 路由 + 导航守卫 |
| HTTP 客户端 | Axios | 请求拦截 + JWT 自动携带 |
| 后端框架 | FastAPI | 高性能异步 Python Web 框架 |
| 数据库 | PostgreSQL 15+ | 企业级关系型数据库 |
| ORM | SQLAlchemy 2.0 | 现代化 ORM |
| 迁移工具 | Alembic | 数据库版本管理 |
| 认证 | JWT + OAuth2 | 无状态身份认证 |
| 部署 | Docker Compose | 容器化一键部署 |

## 功能模块

### 登录页面
- 深海军蓝渐变背景 + 橙色粒子连线动画
- 毛玻璃效果登录卡片
- 近期赛事倒计时展示
- 角色自动跳转（管理员 / 运动员）

### 管理员后台（侧栏分区导航）

| 分区 | 功能 |
|------|------|
| 仪表盘 | 活动照片轮播、统计卡片、出勤率概览、快捷操作入口 |
| 运动员管理 | 增删改查、姓名搜索、分组过滤 |
| 训练管理 | 训练课程卡片、日期/时间/地点管理、二维码生成 |
| 考勤管理 | 按课次筛选、出勤/迟到/缺勤/请假、手动与扫码记录 |
| 成绩录入 | 按项目/运动员多维过滤、官方/训练成绩分类 |
| 排名查看 | 按项目查看排行榜、前三名奖牌标识 |
| 项目管理 | 计时/计距类型、性别限制配置 |
| 评分管理 | 态度/出勤/表现三维评分、评语反馈 |
| 训练内容 | 按类别/强度筛选训练计划 |
| 设置 (⚙️) | 个人信息、修改密码、退出登录 |

### 运动员端（移动端底部导航 + PC 侧栏）

| 页面 | 功能 |
|------|------|
| 我的主页 | 个人信息卡片、成绩/出勤/评分统计概览 |
| 我的成绩 | 查看所有比赛和训练成绩 |
| 我的考勤 | 出勤/迟到/缺勤统计、历史记录 |
| 我的评分 | 教练评分详情、三维进度条、评语 |
| 扫码签到 | 输入签到码完成签到 |

### 响应式适配

| 设备 | 布局策略 |
|------|----------|
| PC (≥1024px) | 240px 侧边栏 + 主内容区 |
| 平板 (640-1023px) | 可折叠侧栏 + 自适应网格 |
| 手机 (<640px) | 底部导航栏 + 全宽卡片 + 安全区适配 |

## 项目结构

```
├── app/                          # 后端 Python 代码
│   ├── main.py                   # FastAPI 入口，SPA 路由
│   ├── core/
│   │   ├── config.py             # 环境变量配置
│   │   └── security.py           # JWT + 密码哈希
│   ├── db/
│   │   ├── base.py               # SQLAlchemy Base
│   │   └── session.py            # 数据库连接
│   ├── models/                   # ORM 模型 (9 张表)
│   ├── schemas/                  # Pydantic 校验模型
│   ├── api/
│   │   ├── deps.py               # 依赖注入（认证、权限）
│   │   └── routes/               # API 路由 (11 个模块)
│   └── services/                 # 业务逻辑
├── vue-frontend/                 # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/index.ts          # Axios API 封装
│   │   ├── router/index.ts       # Vue Router 路由配置
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── types/index.ts        # TypeScript 类型定义
│   │   ├── views/
│   │   │   ├── LoginView.vue     # 登录页（粒子动画）
│   │   │   ├── admin/            # 管理员 9 个视图
│   │   │   └── athlete/          # 运动员 5 个视图
│   │   ├── components/           # 公共组件（设置面板等）
│   │   ├── index.css             # 设计系统（色彩/阴影/动画）
│   │   └── App.vue               # 根组件
│   ├── public/images/            # 活动照片素材
│   ├── tailwind.config.ts        # Tailwind 主题扩展
│   └── vite.config.ts            # Vite 配置（代理 API）
├── scripts/
│   └── seed_data.py              # 数据库初始化脚本
├── alembic/                      # 数据库迁移
├── docker-compose.yml            # Docker 编排
├── requirements.txt              # Python 依赖
└── README.md
```

## 运行环境

- Python 3.11+
- Node.js 18+（前端构建）
- PostgreSQL 15+（Docker 推荐）

## 安装与启动

### 1. 后端

```bash
# 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env            # 按需修改数据库连接

# 启动 PostgreSQL
docker compose up -d postgres

# 初始化数据库（含示例数据）
python scripts/seed_data.py

# 启动后端服务
uvicorn main:app --reload --port 8001
```

### 2. 前端

```bash
cd vue-frontend

# 安装依赖
npm install

# 开发模式（自动代理 API 到后端 8001 端口）
npm run dev

# 生产构建（输出到 dist/，由 FastAPI 直接服务）
npm run build
```

### 3. 生产部署

```bash
# 构建前端
cd vue-frontend && npm run build && cd ..

# FastAPI 自动服务 vue-frontend/dist/
uvicorn main:app --host 0.0.0.0 --port 8001
```

或使用 Docker：

```bash
docker compose build
docker compose up -d
```

## 体验账号

| 角色 | 账号 | 密码 | 说明 |
|------|------|------|------|
| 管理员 | `admin` | `Admin123!` | 全部管理权限 |
| 运动员 | `2023001` | `123456` | 短跑组示例 |
| 运动员 | `2023002` | `123456` | 中长跑组示例 |

> 登录后请及时修改密码。

## 访问路径

| 模式 | 地址 | 说明 |
|------|------|------|
| 开发模式 | `http://localhost:3000` | Vite 开发服务器，API 自动代理 |
| 生产模式 | `http://localhost:8001` | FastAPI 服务 SPA + API |
| API 文档 | `http://localhost:8001/docs` | Swagger 自动生成 |

## 设计系统

所有视觉样式通过 CSS 变量统一管理，定义在 `vue-frontend/src/index.css`：

- **主色**: 深海军蓝 `hsl(220 65% 18%)` — 信任、专业
- **强调色**: 活力橙 `hsl(24 95% 53%)` — 能量、运动
- **圆角**: 12px / 8px / 6px 三级体系
- **阴影**: 卡片阴影、悬浮阴影、辉光阴影
- **动画**: 淡入、上滑、缩放、浮动、渐变位移

扩展颜色或样式时，修改 `index.css` 中的 CSS 变量和 `tailwind.config.ts` 中的主题配置即可全局生效。

## 常见问题

1. **登录失败 / Token 过期**：浏览器控制台清空 `localStorage` 后重新登录
2. **端口冲突**：修改 `vite.config.ts` 中的 `server.port` 或启动命令的 `--port` 参数
3. **重置数据库**：`docker compose down -v` 后重新运行 `python scripts/seed_data.py`
4. **前端开发 API 代理**：`vite.config.ts` 已配置 `/api` 代理到 `http://127.0.0.1:8001`

## 数据库配置

- `.env` 预设 `DB_ENGINE=postgresql+psycopg2`、`DB_HOST=localhost`、`DB_PORT=5432`
- 连接串示例：`postgresql+psycopg2://admin:123456@localhost:5432/athletics`
- Alembic 迁移：`alembic upgrade head`
