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
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import Session
from app.bot.modules.absences.models import *
from app.bot.modules.students.models import Student
import json
from app.bot.utils.callbacks import Base
from app.bot.utils import decorators as d
from app.bot.locales import get_text as _
from app.bot.utils.types import Keyboard, Button
from app.bot.modules.students.callbacks import StudentCallback

logger = logging.getLogger(__name__)

def is_user_exist(db, user_id) -> bool:
    teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == user_id))
    return bool(teacher)


class AbsencesCallbacks(Base):

    @d.callbacks.command(command='absences')
    async def entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_message:
            try:
                update.effective_message.delete()
            except Exception as e:
                logger.error(str(e))

        keyboard: Keyboard = [[Button(_('buttons.absences.do.fill'), callback_data=f'fill_absences')],]
                            #   [Button(_('buttons.absences.do.stats'), callback_data=''), Button(_('buttons.absences.do.edit'), callback_data='')]]
        await update.message.reply_text(_('texts.absences.do'),
                                        reply_markup=InlineKeyboardMarkup(keyboard))



class FillAbsencesCallbacks(Base):
    
    @d.callbacks.query(pattern=r'fill_absences')
    # TODO: Сделать чтобы имя у query автогенерировалось на основе класса и название метода, + можно изменить если захочешь
    # через декоратор
    async def fill(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        keyboard: Keyboard = [[Button(_('buttons.absences.fill.today', 
                                        date=datetime.today().strftime('%d.%m.%y')), callback_data=r'fill_today')]]
                            #   [Button(_('buttons.absences.fill.another'))]]
        await query.edit_message_text(text=_('texts.absences.fill.date'),
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        
    @d.callbacks.query(pattern=r'fill_today')
    async def fill_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        date_by_context = context.user_data.get('choosen_day', None) 
        if not date_by_context:
            date_by_context = datetime.now().date()
            context.user_data['choosen_day'] = date_by_context

        data = query.data.replace('fill_today', '')

        with self._get_session(context.application) as s:
            school_day = s.scalar(select(SchoolDay).where(SchoolDay.day==date_by_context and SchoolDay.teacher_id==update.effective_user.id))
                    
            if data == '': 
                if not school_day: 
                    keyboard: Keyboard = []
                    for i in range(1, 11):
                        if i % 3 == 1:
                            keyboard.append([])
                        keyboard[-1].append(InlineKeyboardButton(str(i), callback_data=f"fill_today{i}"))
                    await query.edit_message_text(text=_('texts.absences.fill.count'),
                                                reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                #
            else: 
                try: 
                    data = int(data)
                    school_day = SchoolDay(teacher_id=update.effective_user.id,
                                           day=date_by_context,
                                           lessons=data)
                    s.add(school_day)
                except Exception as e:
                    logger.error(str(e))

            # school day exactly exist 
            context.user_data['school_day'] = school_day
            await query.edit_message_text(text=_('texts.absences.fill.student'),
                                          reply_markup=InlineKeyboardMarkup(StudentCallback._students_in_keyboard(context.application,
                                                                                                                   update.effective_user.id,
                                                                                                                   prefix='fill-student-absences_',
                                                                                                                   info='absences',
                                                                                                                   context=context)[:-1]))
    
    @d.callbacks.query(pattern=r'fill-student-absences_')
    async def student_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        student_id = query.data.replace('fill-student-absences_', '')
        with self._get_session(context.application) as s:
            student = s.scalar(select(Student).where(Student.id == student_id))
            context.user_data['student-absences'] = student

        # TODO: сделать динамическдое добавление причинных кнопок
        keyboard: Keyboard = [[Button(text=_(f'buttons.absences.fill.reason.{reason}'), callback_data=f'fill-student-absences-reason_{reason}') 
                               for reason in ['excused', 'sick', 'cut']],
                               [Button(text=_('buttons.absences.fill.back'), callback_data=r'fill_today')]]
        await query.edit_message_text(text=_('texts.absences.fill.reason', name=student.name),
                                      parse_mode='MarkdownV2',
                                      reply_markup=InlineKeyboardMarkup(keyboard))
        
    @d.callbacks.query(pattern=r'fill-student-absences-reason_')
    async def reason_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        reason = query.data.replace('fill-student-absences-reason_', '')
        context.user_data['student-absences-reason'] = reason
        student = context.user_data.get('student-absences', None)

        if not student:
            # TODO: дореализовать если нет выбора (перезапуск скорее всего)
            return
        
        keyboard: Keyboard = [
            [Button(_('buttons.absences.fill.lessons.all'), callback_data='fill-student-absences-all_lessons')],
            [Button(_('buttons.absences.fill.lessons.choose'), callback_data='fill-student-absences-specify_count')],
        ] 
        await query.edit_message_text(text=_('texts.absences.fill.skips', name=student.name, reason=_(f'buttons.absences.fill.reason.{reason}')),
                                      parse_mode='MarkdownV2',
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    @d.callbacks.query(pattern=r'fill-student-absences-all_lessons|fill-student-absences-specify_count|fill-student-absences-count_')
    async def absences_count(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        student = context.user_data.get('student-absences', None)
        reason = context.user_data.get('student-absences-reason')
        school_day = context.user_data.get('school_day')


        if 'all_lessons' in query.data or 'count_' in query.data:
            if 'count_' in query.data:
                absences: int = int(query.data.rsplit('_')[1])
            else:
                absences: int = school_day.lessons

            with self._get_session(context.application) as s:
                absence = Absence(student_id=student.id,
                                  schoolday_id=school_day.id,
                                  number=absences,
                                  reason=reason)
                s.add(absence)

            
            opts = {
                'count': absences,
                'name': student.name,
                'reason': _(f'buttons.absences.fill.reason.{reason}'),
            }
            keyboard: Keyboard = [[Button(_('buttons.absences.fill.back'), callback_data='fill_today')]]
            await query.edit_message_text(text=_('texts.absences.fill.success', **opts),
                                          parse_mode='MarkdownV2',
                                          reply_markup=InlineKeyboardMarkup(keyboard))
            return
        

        if 'specify_count' in query.data:
            keyboard: Keyboard = []
            for i in range(1, school_day.lessons+1):
                if i%3==1:
                    keyboard.append([])
                keyboard[-1].append(Button(str(i), callback_data=f'fill-student-absences-count_{i}'))

            keyboard.append([Button(_('buttons.absences.fill.lessons.all'), callback_data='fill-student-absences-all_lessons')],)
            await query.edit_message_text(text=_('texts.absences.fill.skips_count'), 
                                          reply_markup=InlineKeyboardMarkup(keyboard))
            return


        
