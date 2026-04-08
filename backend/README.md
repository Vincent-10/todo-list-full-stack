# Todo-List Backend API

基于 FastAPI 构建的 Todo-List 后端 API 服务，支持用户认证、任务管理、分类和标签功能。

## 技术栈

- **框架**: FastAPI 0.109.2
- **数据库**: MySQL 8.0+ (异步连接)
- **ORM**: SQLAlchemy 2.0 (异步模式)
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)
- **数据验证**: Pydantic 2.x

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # 依赖注入（认证等）
│   │   └── v1/
│   │       ├── __init__.py  # API 路由聚合
│   │       ├── auth.py      # 认证接口
│   │       ├── categories.py # 分类接口
│   │       ├── tags.py      # 标签接口
│   │       └── tasks.py     # 任务接口
│   ├── core/
│   │   ├── config.py        # 配置管理
│   │   └── security.py      # 安全工具
│   ├── db/
│   │   └── database.py      # 数据库连接
│   ├── models/
│   │   └── models.py        # SQLAlchemy 模型
│   ├── schemas/
│   │   └── schemas.py       # Pydantic 模式
│   └── main.py              # 应用入口
├── requirements.txt          # 依赖列表
├── .env.example              # 环境变量示例
└── README.md
```

## 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息：

```env
DATABASE_URL=mysql+aiomysql://用户名:密码@localhost:3306/todolist
SECRET_KEY=你的密钥-生产环境请修改
```

### 4. 初始化数据库

使用项目根目录下的 `database/schema.sql` 文件初始化数据库：

```bash
mysql -u root -p < ../database/schema.sql
```

### 5. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 认证 (Authentication)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 |

### 分类 (Categories)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/categories` | 获取所有分类 |
| POST | `/api/v1/categories` | 创建分类 |
| GET | `/api/v1/categories/{id}` | 获取分类详情 |
| PUT | `/api/v1/categories/{id}` | 更新分类 |
| DELETE | `/api/v1/categories/{id}` | 删除分类 |

### 标签 (Tags)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/tags` | 获取所有标签 |
| POST | `/api/v1/tags` | 创建标签 |
| GET | `/api/v1/tags/{id}` | 获取标签详情 |
| PUT | `/api/v1/tags/{id}` | 更新标签 |
| DELETE | `/api/v1/tags/{id}` | 删除标签 |

### 任务 (Tasks)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/tasks` | 获取任务列表（支持过滤） |
| POST | `/api/v1/tasks` | 创建任务 |
| GET | `/api/v1/tasks/{id}` | 获取任务详情 |
| PUT | `/api/v1/tasks/{id}` | 更新任务 |
| DELETE | `/api/v1/tasks/{id}` | 删除任务 |
| PATCH | `/api/v1/tasks/{id}/toggle-star` | 切换星标状态 |
| PATCH | `/api/v1/tasks/{id}/complete` | 标记为完成 |

### 任务过滤参数

`GET /api/v1/tasks` 支持以下查询参数：

- `status`: 任务状态 (0-待完成, 1-进行中, 2-已完成, 3-已取消)
- `priority`: 优先级 (0-无, 1-低, 2-中, 3-高, 4-紧急)
- `category_id`: 分类ID
- `is_starred`: 是否星标 (true/false)
- `search`: 搜索关键词（标题和描述）
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）

## 认证说明

除了注册和登录接口外，其他所有接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <your_token>
```

## 数据模型

### 任务状态 (TaskStatus)

- `0` - 待完成 (PENDING)
- `1` - 进行中 (IN_PROGRESS)
- `2` - 已完成 (COMPLETED)
- `3` - 已取消 (CANCELLED)

### 任务优先级 (TaskPriority)

- `0` - 无优先级 (NONE)
- `1` - 低 (LOW)
- `2` - 中 (MEDIUM)
- `3` - 高 (HIGH)
- `4` - 紧急 (URGENT)

## 开发说明

### 代码风格

项目遵循 PEP 8 规范，建议使用以下工具：

```bash
pip install black isort flake8
black app/
isort app/
flake8 app/
```

### 测试

```bash
pip install pytest pytest-asyncio httpx
pytest
```

## License

MIT
