from typing import List
from sqlalchemy import select, update as upd
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes,
    Application,
    filters,
    ConversationHandler
)
from app.bot.markly.models import Teacher
from app.bot.students.models import Student
from app.bot import messages as msg
from app.bot.utils.callbacks import Base
from app.bot.utils import decorators as d

from datetime import datetime

import logging
l = logging.getLogger(__name__)

Keyboard = List[List[InlineKeyboardButton]]

EDIT_NAME = 101

class StudentCallback(Base):

    model = Student

    @d.callbacks.command(command='my_students')
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.students_list(update, context) 
    
    @d.callbacks.query(pattern=r'student-edit_')
    async def edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        student_id = query.data.replace('student-edit_', '')
        selected_student: Student = context.user_data.get('student', {}).get('selected')
        if not selected_student:
            with self._get_session(context.application) as s:
                selected_student = s.scalar(select(Student).where(Student.teacher_id == update.effective_user.id))

        if not '_' in str(student_id):
            keyboard = [
                [InlineKeyboardButton('edit name', callback_data=f'student-edit_name_{student_id}')],
                [InlineKeyboardButton('back to student', callback_data=f'student_{student_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f'edit {selected_student.name} info',
                                          parse_mode='Markdown',
                                          reply_markup=reply_markup)

        if 'name' in student_id:
            await context.bot.send_message(chat_id=query.message.chat.id,
                                           text=f"send name for your {selected_student.name} student")
            return EDIT_NAME

    @d.callbacks.message(filters=filters.TEXT & ~filters.COMMAND)
    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        new_student_name = update.message.text
        student = context.user_data.get('student', {}).get('selected')
        if not student:
            l.debug(f'not students sry ...')
            return ConversationHandler.END

        with self._get_session(context.application) as s:
            s.execute((upd(Student).where(Student.id==student.id).values(name=new_student_name)))

            keyboard = [[InlineKeyboardButton('back list', callback_data='students-list'),
                         InlineKeyboardButton('back student', callback_data=f'student_{student.id}')]]

            await update.message.reply_text(text="succes",
                                            reply_markup=InlineKeyboardMarkup(keyboard))
            return ConversationHandler.END

        await update.message.edit_text(text="soryy... something wrong")

    @d.callbacks.query(pattern=r'student-delete_')
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        selected_student: Student = context.user_data.get('student').get('selected')
        name: str = selected_student.name

        if selected_student:
            with self._get_session(context.application) as s:
                s.delete(selected_student)
                context.user_data['student']['selected'] = None

        keyboard = [[InlineKeyboardButton('back', callback_data='students-list')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f'{name} student was deleted',
                                      parse_mode='Markdown',
                                      reply_markup=reply_markup)


    @d.callbacks.query(pattern=r'student_')
    async def get(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        student_id: int = int(query.data.replace('student_', ''))

        with self._get_session(context.application) as s:
            context.user_data['student'] = { 'selected': s.scalar(select(Student).where(Student.id == student_id))}
        # TODO: либо блокать удаление когда есть записи связные либо предупреждать и удалять все связанные записи
        keyboard = [
            [
                InlineKeyboardButton('edit', callback_data=f'student-edit_{student_id}'),
                InlineKeyboardButton('delete', callback_data=f'student-delete_{student_id}')],
            [InlineKeyboardButton('back', callback_data='students-list')]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f'student: {context.user_data.get('student').get('selected').name}',
                                      parse_mode='Markdown',
                                      reply_markup=reply_markup)

    @d.callbacks.query(pattern=r'students-list')
    async def students_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        # await query.answer() # comment cuz it's entry point ofcs

        reply_markup = InlineKeyboardMarkup(self._students_in_keyboard(context.application, update.effective_user.id)) 
        data = {'text': 'choose student:',
                'reply_markup': reply_markup}
        await (query.edit_message_text(**data) if query else update.message.reply_text(**data))

    def _students_in_keyboard(self, app: Application, user_id: str) -> Keyboard:
        keyboard: Keyboard = []
        with self._get_session(app) as session:
            cur_stroke: int = -1  
            teacher = session.scalar(select(Teacher).where(Teacher.telegram_id == user_id))
            if not teacher:
                return []
            
            students = teacher.students
            for idx, student in enumerate(students):
                name: str = student.name
                if idx%3 == 0:
                    keyboard.append([])
                    cur_stroke += 1
                keyboard[cur_stroke].append(InlineKeyboardButton(name, callback_data='student_' + str(student.id)))

        return keyboard