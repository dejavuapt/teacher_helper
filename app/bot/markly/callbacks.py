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
import json

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
            context.user_data['school_day'] = school_day
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
                    context.user_data['school_day'] = school_day
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

async def student_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)

    student_id: int = int(query.data.replace('student_', ''))
    with db_scope() as db:
        context.user_data['current_student'] = db.scalar(select(Student).where(Student.id==student_id))

    keyboard = [
        [InlineKeyboardButton(text=f"{reason}", callback_data=f"reason_{key}") for key, reason in msg.REASONS_MAP.items()] 
        ,[InlineKeyboardButton(msg.BACK_TO, callback_data="back2show_students")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=msg.REASON_Q.format(name=context.user_data.get('current_student').name),
        parse_mode="Markdown",
        reply_markup=reply_markup)

async def reason_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    reason = query.data.replace("reason_", "")
    student = context.user_data.get('current_student')

    reason_choosed: str = msg.REASONS_MAP.get(reason)
    context.user_data['reason_choosed'] = reason
    
    keyboard = [
        [InlineKeyboardButton(msg.ALL_LESSONS_BTN, callback_data="all_lessons")],
        [InlineKeyboardButton(msg.CHOOSE_COUNT_BTN, callback_data="specify_count")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        msg.REASON_SKIPS_Q.format(name=student.name, reason=reason_choosed),
        reply_markup=reply_markup
    )

async def show_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard: List[List[InlineKeyboardButton]] = []
    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
    with db_scope() as db:
        cur_stroke: int = -1  
        for idx, student in enumerate(context.user_data.get('students')):
            name: str = student.name
            day: SchoolDay = context.user_data.get('school_day')
            absences_by_day: Absence = db.scalar(select(Absence).where(Absence.schoolday_id==day.id).where(Absence.student_id==student.id))
            if absences_by_day:
                name += f" {absences_by_day.number}/{day.lessons}"
            if idx%3 == 0:
                keyboard.append([])
                cur_stroke += 1
            keyboard[cur_stroke].append(InlineKeyboardButton(name, callback_data='student_' + str(student.id)))

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


async def skipped_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()


    db_scope: Callable[..., Session] = context.application.bot_data.get('db', None)
    
    student = context.user_data.get('current_student')
    reason = context.user_data.get('reason_choosed')
    reason_converted = msg.REASONS_MAP.get(reason)
    school_day = context.user_data.get('school_day')
    base_keyboard: list[Any] = [InlineKeyboardButton(
        msg.BACK_TO, callback_data="back2show_students"
    )]
    
    if query.data == 'all_lessons' or 'count_' in query.data:
        if 'count_' in query.data:
            absences: int = int(query.data.replace("count_", ""))
        else:
            absences: int = context.user_data.get("total_lessons", 0)
        with db_scope() as db:
            absence = Absence(student_id=student.id,
                              schoolday_id=school_day.id,
                              number=absences,
                              reason=reason)
            db.add(absence)
        
        await query.edit_message_text(
            text=msg.ABSENCES_ADD_TXT.format(absences=absences, 
                                             name=student.name,
                                             reason=reason_converted),
            reply_markup=InlineKeyboardMarkup([base_keyboard])
        )
        return
        
    if query.data == 'specify_count':
        keyboard: list[list[InlineKeyboardButton]] = []
        for i in range(1, context.user_data.get('total_lessons')+1):
            if i % 3 == 1:
                keyboard.append([])
            keyboard[-1].append(InlineKeyboardButton(str(i), callback_data=f"count_{i}"))
            
        keyboard.append([InlineKeyboardButton("Все уроки", callback_data="all_lessons")])
        await query.edit_message_text(
            text=f"{student.name} \n Выбери кол-во пропущенных уроков:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return