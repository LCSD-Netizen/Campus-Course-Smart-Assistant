"""业务模块共享的模型、配置和通用辅助函数。"""

import json
from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import engine, SessionLocal
from backend.models.entities import (
    Base,
    Course,
    Document,
    Enrollment,
    Task,
    User,
    Plan,
)
from backend.schemas.requests import (
    ChatBody,
    CourseAccessBody,
    Credentials,
    PlanBody,
    RegisterBody,
    TaskBody,
    UserRoleBody,
)
from backend.core.config import (
    admin_only,
    call_mcp_tool,
    get_db,
    get_user,
    password_hash,
    signed_user_context,
    token_for,
    verify_password,
)


def course_json(course: Course) -> dict[str, Any]:
    """将课程数据库实体转换为前端使用的字典结构。"""
    return {
        "id": course.id,
        "name": course.name,
        "teacher": course.teacher,
        "room": course.room,
        "weekday": course.weekday,
        "start_time": course.start_time,
        "end_time": course.end_time,
        "weeks": course.weeks,
        "credits": course.credits,
        "color": course.color,
    }


def task_json(task: Task, db: Session) -> dict[str, Any]:
    """将任务实体转换为接口响应，并附上课程和截止天数。"""
    course = db.get(Course, task.course_id) if task.course_id else None
    return {
        "id": task.id,
        "title": task.title,
        "kind": task.kind,
        "due_date": task.due_date.isoformat(),
        "completed": task.completed,
        "course_id": task.course_id,
        "course_name": course.name if course else "个人计划",
        "days_left": (task.due_date - date.today()).days,
    }


def seed_data() -> None:
    """创建数据库表，并在空库中写入本地演示数据。"""
    Base.metadata.create_all(engine)

    with SessionLocal() as db:
        demo_exists = db.scalar(
            select(User).where(User.username == "demo")
        )
        if demo_exists:
            return

        student = User(
            username="demo",
            display_name="林知夏",
            password_hash=password_hash("demo1234"),
            role="student",
        )
        admin = User(
            username="admin",
            display_name="管理员",
            password_hash=password_hash("admin1234"),
            role="admin",
            department="校园管理",
        )
        db.add_all([student, admin])
        db.flush()

        # 演示课程用于首次启动后的课表和知识库体验。
        courses = [
            Course(
                name="数据结构与算法",
                teacher="王建国",
                room="理科楼 302",
                weekday=1,
                start_time="08:00",
                end_time="09:40",
                color="blue",
            ),
            Course(
                name="计算机网络",
                teacher="李文清",
                room="信息楼 205",
                weekday=2,
                start_time="10:00",
                end_time="11:40",
                color="green",
            ),
            Course(
                name="操作系统原理",
                teacher="陈思远",
                room="理科楼 410",
                weekday=3,
                start_time="14:00",
                end_time="15:40",
                credits=4,
                color="orange",
            ),
            Course(
                name="数据库系统",
                teacher="赵明",
                room="信息楼 318",
                weekday=4,
                start_time="08:00",
                end_time="09:40",
                color="purple",
            ),
            Course(
                name="软件工程",
                teacher="刘老师",
                room="科创中心 201",
                weekday=5,
                start_time="10:00",
                end_time="11:40",
                credits=2,
                color="green",
            ),
            Course(
                name="大学英语（四）",
                teacher="周敏",
                room="外语楼 106",
                weekday=5,
                start_time="14:00",
                end_time="15:40",
                credits=2,
                color="blue",
            ),
        ]
        db.add_all(courses)
        db.flush()

        for course in courses:
            db.add(Enrollment(user_id=student.id, course_id=course.id))

        # 示例待办与课程讲义让新用户可以直接体验核心功能。
        db.add_all(
            [
                Task(
                    user_id=student.id,
                    course_id=courses[0].id,
                    title="第 5 章编程作业",
                    kind="作业",
                    due_date=date.today() + timedelta(days=1),
                ),
                Task(
                    user_id=student.id,
                    course_id=courses[1].id,
                    title="Wireshark 实验报告",
                    kind="实验报告",
                    due_date=date.today() + timedelta(days=3),
                ),
                Task(
                    user_id=student.id,
                    course_id=courses[2].id,
                    title="期中测验",
                    kind="考试",
                    due_date=date.today() + timedelta(days=5),
                ),
                Task(
                    user_id=student.id,
                    course_id=courses[3].id,
                    title="SQL 查询练习",
                    kind="作业",
                    due_date=date.today() + timedelta(days=7),
                ),
            ]
        )
        db.add_all(
            [
                Document(
                    course_id=courses[0].id,
                    filename="数据结构课程讲义.pdf",
                    uploaded_by=admin.id,
                    content=(
                        "第三章 栈与队列。栈是一种后进先出（LIFO）的线性数据结构，"
                        "基本操作包括入栈、出栈和取栈顶。队列是一种先进先出（FIFO）的"
                        "线性数据结构，循环队列通过取模运算复用数组空间。栈的典型应用"
                        "包括括号匹配、表达式求值和函数调用；队列常用于任务调度和广度优先搜索。"
                    ),
                ),
                Document(
                    course_id=courses[1].id,
                    filename="计算机网络课程讲义.pdf",
                    uploaded_by=admin.id,
                    content=(
                        "传输层提供端到端通信。TCP 面向连接，通过序列号、确认应答和重传"
                        "实现可靠、有序的数据传输；UDP 无连接，不保证送达和顺序，但开销较小、"
                        "延迟较低。文件传输通常使用 TCP，实时音视频和 DNS 常使用 UDP。"
                    ),
                ),
                Document(
                    course_id=courses[2].id,
                    filename="操作系统复习提纲.pdf",
                    uploaded_by=admin.id,
                    content=(
                        "操作系统期中复习重点：进程与线程的状态转换和调度算法；同步互斥、"
                        "信号量与经典同步问题；内存分页、虚拟内存和页面置换算法。"
                    ),
                ),
            ]
        )
        db.commit()


def event(name: str, data: Any) -> str:
    """把事件名称和数据编码为一条标准 SSE 消息。"""
    return (
        f"event: {name}\n"
        f"data: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
    )
