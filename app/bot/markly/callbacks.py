from typing import Any, Final
from datetime import datetime
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

async def markly(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    today_stroke: str = datetime.today().strftime("%d.%m.%Y")
    context.user_data['day'] = today_stroke
    await update.message.reply_markdown(
        msg.FILL_LESSON_GAPS_Q.format(d=today_stroke)
    )
    return states.RECEIVE_DAYS

daily_blanks = markly

async def lessons_per_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        total_lessons: int = int(update.message.text)
        context.user_data["total_lessons"] = total_lessons
        await update.message.reply_markdown(
            msg.FILL_LESSON_GAPS_OK.format(lessons=total_lessons, 
                               date=context.user_data.get('day'))
        )
        # TODO: Тут крч нужно инциализировать студентов и сунуть их в данных пользователя, пусть ходят с ним по
        # конверсам, а не каждый раз к бд делать запрос
        context.user_data['students_list'] = ['dolbev', 'da', 'pidoraz']
        await show_students(update, context)
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
        [InlineKeyboardButton(f'{student}', callback_data=f'student_{student}') 
         for student in context.user_data.get('students_list')]
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