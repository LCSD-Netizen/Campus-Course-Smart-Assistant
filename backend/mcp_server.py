"""Private Streamable HTTP MCP service. Start with `python -m backend.mcp_server`.

Every tool requires an HMAC-signed identity issued by the API process. The LLM
never receives or chooses a user id; the API binds the signed context to the
authenticated request before the MCP call.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import date

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from backend.main import Course, Enrollment, Plan, SessionLocal, Task, User, course_json, search_materials

load_dotenv()
mcp = FastMCP("campus-course-tools", host=os.getenv("MCP_HOST", "127.0.0.1"), port=int(os.getenv("MCP_PORT", "8001")))


def verified_user(context: str) -> int:
    try:
        user_text, signature = context.split(".", 1)
        expected = hmac.new(os.getenv("SECRET_KEY", "development-only-change-this-secret").encode(), user_text.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected): raise ValueError("signature")
        return int(user_text)
    except Exception as exc:
        raise ValueError("未授权的用户上下文") from exc


@mcp.tool()
async def get_my_schedule(auth_context: str) -> str:
    """查询当前登录学生本人有权限访问的课表。"""
    user_id = verified_user(auth_context)
    with SessionLocal() as db:
        rows = db.scalars(select(Course).join(Enrollment).where(Enrollment.user_id == user_id).order_by(Course.weekday, Course.start_time)).all()
        return json.dumps([course_json(row) for row in rows], ensure_ascii=False)


@mcp.tool()
async def search_course_materials(auth_context: str, query: str) -> str:
    """在当前学生已选课程的 RAG 知识库中检索资料片段。"""
    user_id = verified_user(auth_context)
    with SessionLocal() as db:
        user = db.get(User, user_id)
        if not user: raise ValueError("用户不存在")
        rows = await search_materials(query, user, db)
        return json.dumps(rows, ensure_ascii=False)


@mcp.tool()
async def save_study_plan(auth_context: str, title: str, content: str, due_date: str = "") -> str:
    """将学习计划保存到当前登录学生的个人计划。"""
    user_id = verified_user(auth_context)
    parsed = date.fromisoformat(due_date) if due_date else None
    with SessionLocal() as db:
        row = Plan(user_id=user_id, title=title, content=content, due_date=parsed)
        db.add(row); db.commit(); db.refresh(row)
        return json.dumps({"id": row.id, "title": row.title, "saved": True}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
