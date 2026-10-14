# 知课 · 校园课程智能助手

Vue 3 + FastAPI 全栈校园课程助手。学生登录后可查看本人课表、管理作业、向课程资料提问，并生成和保存学习计划。管理员可管理账户角色、为指定课程上传资料。FastAPI 使用 LangChain 工具编排 Agent，通过独立 FastMCP 服务访问有权限的课表、RAG 检索和个人计划；对话过程使用 SSE 实时推送到前端。

## 技术结构

- 前端：Vue 3、Vite、Element Plus、Axios
- 业务 API：FastAPI、SQLAlchemy、JWT
- Agent：LangChain `create_agent`（LangGraph ReAct-style tool loop，DeepSeek OpenAI-compatible API）
- MCP：FastMCP Streamable HTTP，监听本机 `8001`
- RAG：SiliconFlow `BAAI/bge-m3` Embedding + Chroma 持久向量库
- 开发环境数据库：SQLite；配置 `DATABASE_URL` 后可使用 MySQL 8

## 后端目录结构

后端按职责拆分，`backend/main.py` 仅负责创建 FastAPI 应用和挂载路由：

```text
backend/
├── main.py                 # 应用入口与路由注册
├── core/                   # 配置、数据库会话、认证依赖与共享函数
├── models/                 # SQLAlchemy 数据库实体
├── schemas/                # API 请求参数校验
├── api/routers/            # 登录、课程、资料、管理和对话接口
├── services/               # RAG、Agent 和启动索引服务
└── mcp_server.py           # 独立 MCP 工具服务
```

后端模块中的模型、接口和服务函数均配有中文说明；`uvicorn backend.main:app` 的启动命令保持不变。

## 环境

- Node.js LTS
- Python 3.12+
- MySQL 8（可选；本地演示默认使用 SQLite）

首次克隆后安装依赖：

```powershell
# 项目根目录：Python 后端与 MCP 依赖
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# 前端目录：Vue / Vite 依赖
cd frontend
npm install
```

后端从项目根目录读取 `.env`。全新克隆时，将 `.env.example` 复制为 `.env`，再设置 JWT 随机密钥、DeepSeek 与 SiliconFlow API 密钥。密钥只由后端读取，`.env` 已加入 Git 忽略规则。首次启动会建表并写入演示账户、示例课程、待办事项和课程讲义。

## 启动

打开三个 PowerShell 窗口。前两个窗口停留在项目根目录，前端窗口进入 `frontend` 目录：

```powershell
# 窗口 1：MCP 工具服务
.venv\Scripts\Activate.ps1
python -m backend.mcp_server
```

```powershell
# 窗口 2：FastAPI 业务与 Agent 服务
.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

```powershell
# 窗口 3：Vue 前端
cd frontend
npm run dev
```

访问 `http://localhost:5173`。API 文档位于 `http://localhost:8000/docs`。

## 演示账户

- 学生：`demo` / `demo1234`
- 管理员：`admin` / `admin1234`

演示账户仅用于本地开发；部署前请更换口令和 `SECRET_KEY`。若使用 MySQL，先创建数据库：

```sql
CREATE DATABASE campus_course CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后在 `.env` 配置：

```text
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/campus_course?charset=utf8mb4
```

## Agent 与工具权限

`POST /api/chat/stream` 接收 Bearer JWT，并返回 `text/event-stream`。前端显示思考阶段、MCP 工具调用和增量回答。Agent 仅获得不带用户 ID 参数的工具定义；FastAPI 根据登录用户附加 HMAC 签名身份，再访问本机 MCP 服务。MCP 工具验证签名，并在课表、资料检索和学习计划查询中再次按用户身份过滤。没有模型密钥时，系统使用本地规则与示例课程资料提供开发演示响应。

管理员上传的 PDF、DOCX、PPTX、TXT 会提取文本并分块；配置 Embedding 后写入 Chroma，学生只能检索共享资料或本人已选课程对应的资料。当前演示课程用于首次初始化，后续正式项目可按教务数据扩展课程与选课导入。
