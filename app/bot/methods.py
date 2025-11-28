from typing import Any
from datetime import date
import logging
from .states import CHOOSING_STUDENTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# TODO: Time to live of callback query
students: tuple[str, ...] = ("Тестов И.П.", "Русков А.П.", "Новосел Т.П.")
reasons: dict[str, str] = {"valid": "🎓 Увж. причина",
                           "sick": "😷 Болеет", 
                           "not_valid": "🚶 Прогуливает" }


logger = logging.getLogger(__name__)

# TODO: Пускай кол-во уроков будет после вызова команды. Чтобы потом можно было выбирать по классам например
async def daily_blanks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start point to get info about day
    """
    # TODO: check if day exist
    await update.message.reply_markdown(
        f"Давай заполним пропуски за {date.today().strftime("%d.%m.%Y")}!\n"
        "\nСколько сегодня всего уроков?"
    )
    return 0
    
       
async def receive_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text: str = update.message.text
    try:
        # TODO: проверить что не больше 10
        total_lessons: int = int(user_text)
        # TODO: write connect and store data in DB
        # date: 18.09.2025 
        # lessons: 7
        context.user_data["total_lessons"] = total_lessons
        await update.message.reply_markdown(
            text=f"Супер, записала {total_lessons} уроков на {date.today().strftime("%d.%m.%Y")}"
        )
        await show_students(update, context)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_markdown(
            text="😢 Нужно ввести число и тогда мы сможем продолжить!"
        )
        
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_markdown(
        "Хорошо! Пиши снова если потребуется помощь 😉"
    )
    return ConversationHandler.END
    

    
async def show_students(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show and choose a students.
    yes i do dsfsd
    """
    # TODO: get students from DB. 
    # Here need in the DB level check about existing data in db.
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
    context.user_data['current_student'] = {
        "name": student_name
    }
    
    keyboard = [
        [InlineKeyboardButton(text=f"{reason}", callback_data=f"reason_{key}") for key, reason in reasons.items()] 
        ,[InlineKeyboardButton("⬅️ Назад к ученикам", callback_data="back2show_students")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"По какой причине нет {student_name}?",
        parse_mode="Markdown",
        reply_markup=reply_markup)
    
async def reason_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    reason_choosed: str = reasons.get(query.data.replace("reason_", ""))
    student_data = context.user_data.get('current_student')
    student_data['reason'] = reason_choosed
    
    keyboard = [
        [InlineKeyboardButton("Все уроки", callback_data="all_lessons")],
        [InlineKeyboardButton("Указать количество", callback_data="specify_count")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🗿 Ученик: {student_data.get("name")}"
        f"\nПричина: {reason_choosed}"
        "\nСколько пропущенных?",
        reply_markup=reply_markup
    )

async def skipped_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    student_data = context.user_data.get('current_student')
    base_keyboard: list[Any] = [InlineKeyboardButton(
        "⬅️ Вернуться назад к ученикам", callback_data="back2show_students"
    )]
    
    if query.data == 'all_lessons' or 'count_' in query.data:
        if 'count_' in query.data:
            skip_count: int = int(query.data.replace("count_", ""))
        else:
            skip_count: int = context.user_data.get("total_lessons", 0)
        text: str = f"Отмечено {skip_count} уроков для {student_data.get("name")} по причине {student_data.get("reason")}"
        await query.edit_message_text(
            text=text,
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
            text=f"{student_data.get("name")} \n Выбери кол-во пропущенных уроков:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return