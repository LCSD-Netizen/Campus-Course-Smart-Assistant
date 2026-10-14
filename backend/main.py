"""FastAPI 应用入口。业务路由与服务实现在各自模块中。"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 必须先加载项目根目录的环境配置，再导入会初始化数据库的模块。
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.shared import seed_data
from backend.services.startup import index_seed_docs
from backend.api.routers import auth, academic, documents, admin, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表并准备演示数据，再索引已有资料。
    seed_data()
    await index_seed_docs()
    yield

app = FastAPI(
    title="知课校园课程智能助手 API",
    version="1.0.0",
    lifespan=lifespan,
)
origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_routers = (
    auth.router,
    academic.router,
    documents.router,
    admin.router,
    chat.router,
)
for api_router in api_routers:
    app.include_router(api_router)
