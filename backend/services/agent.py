"""校园助手 Agent、离线问答与 SSE 事件编排。"""

from __future__ import annotations
import asyncio
import hashlib
import hmac
import json
import os
import re
import secrets
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncIterator
import httpx
import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, create_engine, delete, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from backend.core.shared import *
from backend.services.rag import search_materials

async def run_agent(message: str, user: User, db: Session) -> AsyncIterator[str]:
    """处理run_agent相关业务逻辑。"""
    yield event('status', {'stage': 'thinking', 'message': '正在理解你的问题'})
    llm_key = os.getenv('OPENAI_API_KEY')
    if not llm_key:
        async for item in offline_agent(message, user, db):
            yield item
        return
    try:
        from langchain.agents import create_agent
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        from langchain_openai import ChatOpenAI

        @tool
        async def get_my_schedule() -> str:
            """查询当前登录学生本人的课程表。不得查询其他用户。"""
            result = await call_mcp_tool('get_my_schedule', {'auth_context': signed_user_context(user.id)})
            if result is not None:
                return result
            courses = db.scalars(select(Course).join(Enrollment).where(Enrollment.user_id == user.id).order_by(Course.weekday, Course.start_time)).all()
            return json.dumps([course_json(c) for c in courses], ensure_ascii=False)

        @tool
        async def search_course_materials(query: str) -> str:
            """在当前学生有权限访问的课程资料中进行 RAG 检索。"""
            result = await call_mcp_tool('search_course_materials', {'auth_context': signed_user_context(user.id), 'query': query})
            return result if result is not None else json.dumps(await search_materials(query, user, db), ensure_ascii=False)

        @tool
        async def save_study_plan(title: str, content: str, due_date: str='') -> str:
            """为当前登录学生保存学习计划。"""
            result = await call_mcp_tool('save_study_plan', {'auth_context': signed_user_context(user.id), 'title': title, 'content': content, 'due_date': due_date})
            if result is not None:
                return result
            parsed = date.fromisoformat(due_date) if due_date else None
            row = Plan(user_id=user.id, title=title, content=content, due_date=parsed)
            db.add(row)
            db.commit()
            db.refresh(row)
            return json.dumps({'id': row.id, 'title': title, 'saved': True}, ensure_ascii=False)
        tools = [get_my_schedule, search_course_materials, save_study_plan]
        llm = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'deepseek-chat'), api_key=llm_key, base_url=os.getenv('OPENAI_BASE_URL', 'https://api.deepseek.com/v1'), temperature=0.2, streaming=True)
        agent = create_agent(model=llm, tools=tools, system_prompt=f'你是校园课程智能助手。只回答当前用户有权限访问的信息。用户称呼：{user.display_name}。需要查课表时调用 get_my_schedule；依据课程资料回答时调用 search_course_materials；用户要求制定并保存计划时先生成计划并调用 save_study_plan。没有资料依据时明确说明。使用简体中文。')
        answer = ''
        labels = {'get_my_schedule': '查询你的课表', 'search_course_materials': '检索课程资料', 'save_study_plan': '保存学习计划'}
        async for item in agent.astream_events({'messages': [HumanMessage(content=message)]}, config={'recursion_limit': 12}, version='v2'):
            kind = item.get('event')
            name = item.get('name', '')
            data = item.get('data', {})
            if kind == 'on_tool_start':
                yield event('tool_start', {'name': name, 'label': labels.get(name, name), 'input': data.get('input', {})})
            elif kind == 'on_tool_end':
                result = data.get('output', '')
                if hasattr(result, 'content'):
                    result = result.content
                yield event('tool_result', {'name': name, 'result': result})
            elif kind == 'on_tool_error':
                yield event('tool_result', {'name': name, 'result': f"工具执行失败：{str(data.get('error', ''))[:250]}"})
            elif kind == 'on_chat_model_stream':
                chunk = data.get('chunk')
                text = getattr(chunk, 'content', '')
                if isinstance(text, list):
                    text = ''.join((block.get('text', '') for block in text if isinstance(block, dict)))
                if isinstance(text, str) and text:
                    answer += text
                    yield event('token', {'text': text})
            elif kind == 'on_chain_end' and isinstance(data.get('output'), dict):
                final_messages = data['output'].get('messages', [])
                if final_messages and (not answer):
                    final_content = getattr(final_messages[-1], 'content', '')
                    if isinstance(final_content, str):
                        answer = final_content
        yield event('done', {'answer': answer})
    except Exception as exc:
        yield event('error', {'message': f'AI 服务暂不可用：{str(exc)[:300]}'})


async def offline_agent(message: str, user: User, db: Session) -> AsyncIterator[str]:
    """处理offline_agent相关业务逻辑。"""
    q = message.lower()
    if any((word in q for word in ('课表', '课程安排', '今天有什么课', '明天有什么课'))):
        label, name = ('查询你的课表', 'get_my_schedule')
        yield event('tool_start', {'name': name, 'label': label, 'input': {}})
        mcp_result = await call_mcp_tool(name, {'auth_context': signed_user_context(user.id)})
        try:
            result = json.loads(mcp_result) if mcp_result is not None else None
        except Exception:
            result = None
        if result is None:
            rows = db.scalars(select(Course).join(Enrollment).where(Enrollment.user_id == user.id).order_by(Course.weekday, Course.start_time)).all()
            result = [course_json(c) for c in rows]
        yield event('tool_result', {'name': name, 'result': result})
        days = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        answer = '这是你本人的课表：\n' + '\n'.join((f"{days[c['weekday']]} {c['start_time']}-{c['end_time']}｜{c['name']}｜{c['room']}" for c in result))
    elif any((word in q for word in ('计划', '规划', '安排学习', '复习计划'))):
        title = '本周学习计划'
        tasks = db.scalars(select(Task).where(Task.user_id == user.id, Task.completed.is_(False)).order_by(Task.due_date)).all()
        lines = [f'- 优先完成「{t.title}」（{t.due_date.isoformat()} 截止）' for t in tasks[:3]] or ['- 整理本周课程笔记并复习重点']
        content = '\n'.join(lines + ['- 每天预留 30 分钟回顾课堂内容', '- 完成后检查并记录疑难问题'])
        yield event('tool_start', {'name': 'save_study_plan', 'label': '保存学习计划', 'input': {'title': title}})
        due = date.today() + timedelta(days=7)
        mcp_result = await call_mcp_tool('save_study_plan', {'auth_context': signed_user_context(user.id), 'title': title, 'content': content, 'due_date': due.isoformat()})
        if mcp_result is None:
            row = Plan(user_id=user.id, title=title, content=content, due_date=due)
            db.add(row)
            db.commit()
            db.refresh(row)
            saved = {'id': row.id, 'saved': True}
        else:
            try:
                saved = json.loads(mcp_result)
            except Exception:
                saved = {'saved': True}
        yield event('tool_result', {'name': 'save_study_plan', 'result': saved})
        answer = f'已为你生成并保存「{title}」：\n{content}'
    else:
        yield event('tool_start', {'name': 'search_course_materials', 'label': '检索课程资料', 'input': {'query': message}})
        mcp_result = await call_mcp_tool('search_course_materials', {'auth_context': signed_user_context(user.id), 'query': message})
        try:
            rows = json.loads(mcp_result) if mcp_result is not None else None
        except Exception:
            rows = None
        if rows is None:
            rows = await search_materials(message, user, db)
        yield event('tool_result', {'name': 'search_course_materials', 'result': rows})
        if rows:
            answer = '根据你的课程资料：\n\n' + '\n\n'.join((f"《{r['filename']}》\n{r['content']}" for r in rows[:3]))
        else:
            answer = '我没有在你有权限访问的课程资料中找到相关内容。可以请管理员上传对应课程资料后再问我。'
    for i in range(0, len(answer), 28):
        await asyncio.sleep(0.025)
        yield event('token', {'text': answer[i:i + 28]})
    yield event('done', {'answer': answer})