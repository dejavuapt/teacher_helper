from typing import Any, Final, List, Callable
from datetime import datetime, date
import logging
from telegram import (
    Update, 
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, 
    ConversationHandler
)
from . import messages as msg, states
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import Session
from app.bot.markly.models import *

logger = logging.getLogger(__name__)

def is_user_exist(db, user_id) -> bool:
    teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == user_id))
    return bool(teacher)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
    with db_scope() as db:
        user_id = update.effective_user.id
        if not is_user_exist(db, user_id):
            new_user = Teacher(telegram_id=user_id)
            db.add(new_user)
            await update.message.reply_markdown(msg.REGISTER_OK)
        else:
            await update.message.reply_markdown(msg.REGISTER_FALL)

async def students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def markly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    day: str = date.today()
    context.user_data['day'] = day

    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
    with db_scope() as db:
        teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == update.effective_user.id))
        if not teacher:
            await update.message.reply_markdown(msg.NO_REGISTRY_ERROR)
            return ConversationHandler.END


        school_day = db.scalar(select(SchoolDay).where(SchoolDay.teacher_id==teacher.id))
        if school_day:
            context.user_data['total_lessons'] = school_day.lessons
            await lessons_per_day(update, context)
            return

    await update.message.reply_markdown(
        msg.FILL_LESSON_GAPS_Q.format(d=day)
    )
    return states.RECEIVE_DAYS

daily_blanks = markly

async def lessons_per_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
        if not context.user_data.get('total_lessons', None):
            total_lessons: int = int(update.message.text)
            context.user_data["total_lessons"] = total_lessons

        day = context.user_data.get('day')
        user_id = update.effective_user.id
        logger.debug(f'User telegram id: {user_id}')
        
        students: List[Student] = []
        with db_scope() as db:
            teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == user_id))
            if teacher:
                school_day = db.scalar(select(SchoolDay).where(SchoolDay.teacher_id==teacher.id))
                if not school_day:
                    school_day = SchoolDay(teacher_id=teacher.id,
                                           day=day,
                                           lessons=total_lessons)
                    db.add(school_day)
                    await update.message.reply_markdown(msg.FILL_LESSON_GAPS_OK.format(lessons=total_lessons, 
                                                                                       date=context.user_data.get('day')))
                else:
                    await update.message.reply_markdown(msg.STUDY_EXIST.format(lessons = school_day.lessons))
                students = teacher.students
            
        if students:
            context.user_data['students'] = students
            await show_students(update, context)
        else:
            await update.message.reply_markdown(
                msg.NO_STUDENTS_ERROR
            )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_markdown(
            msg.FILL_LESSON_GAPS_ERROR
        )

receive_days = lessons_per_day

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # TODO: Если в инлайне, то надо инлайн закрыть а сообщение нахер удалить
    await update.message.reply_markdown(
        msg.CANCEL
    )
    return ConversationHandler.END


    pass

def student_selected():
    pass


def reason_selected():
    pass

async def show_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(f'{student.name}', callback_data=f'student_{student.name}') 
         for student in context.user_data.get('students')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    m_data = {
        "text": msg.CHOOSE_STUDENT,
        "reply_markup": reply_markup
    }
    if query:
        await query.edit_message_text(**m_data)
    else: 
        await update.message.reply_text(**m_data)

def skipped_count():
    pass