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
from app.bot.utils.callbacks import Base
from app.bot.utils import decorators as d

from app.bot.locales import get_text as _

import logging
l = logging.getLogger(__name__)

Keyboard = List[List[InlineKeyboardButton]]

EDIT_NAME = 101

class StudentCallback(Base):

    model = Student

    @d.callbacks.command(command='my_students')
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await self.students_list(update, context) 


    @d.callbacks.query(pattern=r'student-add')
    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        context.user_data['action'] = 'add'
        await query.edit_message_text(text=_('texts.students.add'))
        return EDIT_NAME
    
    
    @d.callbacks.query(pattern=r'student-edit_')
    async def edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()

        context.user_data['action'] = 'edit'
        
        student_id = query.data.replace('student-edit_', '')
        selected_student: Student = context.user_data.get('student', {}).get('selected')
        if not selected_student:
            with self._get_session(context.application) as s:
                selected_student = s.scalar(select(Student).where(Student.teacher_id == update.effective_user.id))

        if not '_' in str(student_id):
            keyboard = [
                [InlineKeyboardButton(_('buttons.students.edits.name'), callback_data=f'student-edit_name_{student_id}')],
                [InlineKeyboardButton(_('buttons.students.backs.single'), callback_data=f'student_{student_id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text= _('texts.students.choosen.edit', name=selected_student.name),
                                          parse_mode='Markdown',
                                          reply_markup=reply_markup)

        if 'name' in student_id:
            await context.bot.send_message(chat_id=query.message.chat.id,
                                           text=_('texts.students.change.name', name=selected_student.name), 
                                           parse_mode='MarkdownV2')
            return EDIT_NAME

    @d.callbacks.message(filters=filters.TEXT & ~filters.COMMAND)
    async def name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        new_student_name = update.message.text
        student = context.user_data.get('student', {}).get('selected')
        action = context.user_data.get('action', '')
        if not student and action == 'edit':
            l.debug(f'not students sry ...')
            return ConversationHandler.END
        if action == 'edit':
            with self._get_session(context.application) as s:
                s.execute((upd(Student).where(Student.id==student.id).values(name=new_student_name)))

                keyboard = [[InlineKeyboardButton(_('buttons.students.backs.deep_list'), callback_data='students-list'),
                            InlineKeyboardButton(_('buttons.students.backs.single'), callback_data=f'student_{student.id}')]]

                await update.message.reply_text(text=_('texts.success.edit'),
                                                reply_markup=InlineKeyboardMarkup(keyboard))
                return ConversationHandler.END
        
        if action == 'add':
            with self._get_session(context.application) as s:
                teacher = s.scalar(select(Teacher).where(Teacher.telegram_id == update.effective_user.id))
                if teacher:
                    st = Student(teacher_id=teacher.id, name=new_student_name)
                    s.add(st)
                    l.debug(f'{str(st)} was successfully created')
                    keyboard: Keyboard = [[InlineKeyboardButton(_('buttons.students.add_more'), callback_data='student-add'),
                                           InlineKeyboardButton(_('buttons.students.backs.list'), callback_data='students-list')]]
                    await update.message.reply_text(text=_('texts.success.add'),
                                                    reply_markup=InlineKeyboardMarkup(keyboard))
                    return ConversationHandler.END

        l.error(f"action: {action}, student: {student}")
        return ConversationHandler.END

    @d.callbacks.query(pattern=r'student-delete_')
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        selected_student: Student = context.user_data.get('student').get('selected')

        if selected_student:
            with self._get_session(context.application) as s:
                s.delete(selected_student)
                del context.user_data['student']['selected']

        keyboard = [[InlineKeyboardButton(_('buttons.students.backs.list'), callback_data='students-list')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=_('texts.students.deleted', name=selected_student.name),
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
                InlineKeyboardButton(_('buttons.students.edits.base'), callback_data=f'student-edit_{student_id}'),
                InlineKeyboardButton(_('buttons.students.delete'), callback_data=f'student-delete_{student_id}')],
            [InlineKeyboardButton(_('buttons.students.backs.list'), callback_data='students-list')]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        name = context.user_data.get('student').get('selected').name
        await query.edit_message_text(text=_('texts.students.choosen.general', name=name),
                                      parse_mode='MarkdownV2',
                                      reply_markup=reply_markup)

    @d.callbacks.query(pattern=r'students-list')
    async def students_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        # await query.answer() # comment cuz it's entry point ofcs

        reply_markup = InlineKeyboardMarkup(self._students_in_keyboard(context.application, update.effective_user.id)) 
        data = {'text': _('texts.students.list'),
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
            in_col = 1
            for idx, student in enumerate(students):
                name: str = student.name
                name = name.split(' ')
                short_name: str = str(name[0]) + ' ' + '.'.join([el.capitalize()[0] for el in name[1:]]) + ('.' if len(name) > 2 else '')
                if idx%in_col == 0:
                    keyboard.append([])
                    cur_stroke += 1
                keyboard[cur_stroke].append(InlineKeyboardButton(short_name, callback_data='student_' + str(student.id)))
        
        keyboard.append([InlineKeyboardButton(text=_('buttons.students.add'), callback_data='student-add')])

        return keyboard