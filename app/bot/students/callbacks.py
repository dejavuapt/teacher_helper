from typing import Callable
from sqlalchemy.orm import Session
from sqlalchemy import select
from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes
)
from app.bot.markly.models import Teacher
from app.bot.students.models import Student
from app.bot import messages as msg

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 0:
        await update.message.reply_markdown(msg.NEED_STUDENTS)
        return
    
    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
    with db_scope() as db:
        teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == update.effective_user.id))
        if teacher:
            for name in args:
                student = Student(teacher_id=teacher.id,
                                  name=name)
                db.add(student)
            await update.message.reply_markdown(msg.FILL_STUDENTS_OK)
        else:
            await update.message.reply_markdown(msg.NO_REGISTRY_ERROR)
            return
        
students = add