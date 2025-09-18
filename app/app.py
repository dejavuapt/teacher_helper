from datetime import date
import logging
from .states import CHOOSING_STUDENTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler


logger = logging.getLogger(__name__)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start point to get info about day
    """
    # TODO: check if day exist
    
    try:
        total_lessons: int = int(context.args[0])
        # TODO: write connect and store data in DB
        # date: 18.09.2025 
        # lessons: 7
        await update.message.reply_markdown(
            text=f"kk, записал {total_lessons} уроков на {date.today().strftime("%d.%m.%Y")}"
        )
        await show_students(update, context)
    except ValueError:
        await update.message.reply_markdown(
            text="😢 нужна цифра, пример: `/today 7`, что означает сегодня 7 уроков"
        )
    except IndexError:
        await update.message.reply_markdown(
            text="😢 ты не ввел(a) сколько уроков будет, например: `/today 7`"
        )
    
async def show_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show and choose a students.
    """
    # TODO: get students from DB
    students: tuple[str, ...] = ("Тестов И.П.", "Русков А.П.", "Новосел Т.П.")
    keyboard = [
        [InlineKeyboardButton(text=f"{student}", callback_data=f"student_{student}") for student in students]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query = update.callback_query
    message_data = {
        "text": "Выбери ученика для которого нужно внести запись",
        "reply_markup": reply_markup
    }
    if query:
        await query.edit_message_text(**message_data)
    else:
        await update.message.reply_text(**message_data)
    
async def student_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    student_name: str = query.data.replace("student_", "")
    
    reasons: list[str] = ["Увж. причина", "Болеет", "Прогуливает"]
    keyboard = [
        [InlineKeyboardButton(text=f"{reason}", callback_data=f"reason_{reason}") for reason in reasons] + [InlineKeyboardButton("<<", callback_data="back2show_students")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"По какой причине нет {student_name}?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
async def reason_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    reason_choosed: str = query.data.replace("reason_", "")
    
    await query.edit_message_text(
        text=f"Ура, ты выбрал: {reason_choosed}"
    )
