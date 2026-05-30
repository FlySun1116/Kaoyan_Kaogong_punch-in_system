# 考研考公学习打卡系统

面向考研、考公备考者的 Web 学习打卡与进度管理工具。支持多用户登录、科目与计划管理、每日打卡、进度监控、统计分析，以及数据备份与导出。

## 功能概览

| 模块 | 说明 |
|------|------|
| **用户认证** | 注册 / 登录 / 退出；按用户隔离数据 |
| **科目管理** | 自定义科目、权重、标识色；注册时按考试类型同步模板科目 |
| **计划管理** | 总 / 月 / 周 / 日四级计划树，支持折叠浏览 |
| **每日打卡** | 记录学习时长与内容；支持补卡（受全局规则限制） |
| **进度监控** | 日 / 周 / 总体完成率，环形图展示 |
| **统计分析** | 打卡率、近 14 天学习趋势折线图、科目维度统计 |
| **数据管理** | JSON 导出、数据库备份与恢复 |
| **管理后台** | 用户启用/禁用、全局配置、操作日志（仅管理员） |

## 技术栈

- **后端**：FastAPI + SQLAlchemy 2.x + SQLite
- **前端**：Bootstrap 5 + Jinja2 + Chart.js + 原生 JavaScript
- **认证**：Session Cookie（Starlette SessionMiddleware）+ passlib 密码哈希

## 快速开始

### 环境要求

- Python 3.10+
- macOS / Linux / Windows

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/FlySun1116/Kaoyan_Kaogong_punch-in_system.git
cd Kaoyan_Kaogong_punch-in_system

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（首次启动会自动建表并写入种子数据）
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：<http://127.0.0.1:8000>

API 文档：<http://127.0.0.1:8000/docs>

### 默认管理员

首次启动会自动创建管理员账号（若不存在）：

| 用户名 | 密码 | 说明 |
|--------|------|------|
| `admin` | `admin123` | 可访问 `/admin` 管理后台 |

> 生产环境部署后请立即修改默认密码。

### 演示数据（可选）

项目提供考研 / 考公两套演示数据，可重复执行：

```bash
.venv/bin/python seed_demo_data.py
```

| 用户名 | 密码 | 考试类型 |
|--------|------|----------|
| `kaoyan_demo` | `demo123` | 考研 |
| `kaogong_demo` | `demo123` | 考公 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Session 签名密钥 | 开发用固定值（**生产环境务必设置**） |

示例：

```bash
export SECRET_KEY="your-random-secret-key"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
Kaoyan_Kaogong_punch-in_system/
├── app/
│   ├── main.py              # 应用入口
│   ├── config.py            # 路径与配置
│   ├── init_db.py           # 数据库初始化与种子
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 校验
│   ├── services/            # 业务逻辑
│   ├── routers/             # API 与页面路由
│   ├── templates/           # Jinja2 页面与 CSS/JS
│   └── static/images/       # 品牌资源（Logo 等）
├── data/                    # SQLite 数据库、备份、导出（不提交 Git）
├── seed_demo_data.py        # 演示数据脚本
├── requirements.txt
└── README.md
```

## 主要页面

| 路径 | 说明 |
|------|------|
| `/` | 学习仪表盘 |
| `/subjects` | 科目管理 |
| `/plans` | 计划管理 |
| `/punch` | 每日打卡 |
| `/progress` | 进度监控 |
| `/stats` | 统计分析 |
| `/data-manage` | 数据备份与导出 |
| `/admin` | 管理后台（管理员） |
| `/login` `/register` | 登录 / 注册 |

## 数据说明

- 数据库文件：`data/Kykg_punch-in_system.db`
- 备份目录：`data/backup/`
- 导出目录：`data/export/`

以上目录已在 `.gitignore` 中忽略，不会上传到 Git 仓库。从备份恢复后需重启 `uvicorn` 使连接生效。

## 开发说明

- 启动时 `init_db` 会自动检测旧版单用户库并备份迁移
- 静态资源：`/static` → 页面 CSS/JS；`/assets` → `app/static/` 下的图片等资源
- 多用户数据通过 `user_id` 外键隔离，普通用户只能访问自己的科目、计划与打卡记录

## License

个人学习项目，按需使用与修改。
