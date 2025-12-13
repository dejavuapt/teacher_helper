from app.bot.utils.callbacks import Base
from app.bot.modules.students.models import Student
from app.bot.modules.absences.models import Absence, SchoolDay, Teacher
from app.bot.utils import decorators as d
from telegram import (
    Update, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, 
)
from sqlalchemy import select
from app.bot.utils.types import Keyboard, Button
from app.bot.locales import get_text as _
import pandas as pd
from io import BytesIO

class StatisticsCallbacks(Base): 

    # @d.callbacks.command(command='get_absences')
    # async def entry(update: Update, context: ContextTypes.DEFAULT_CONTEXT) -> None:
        # keyboard: Keyboard = [[Button()]]

    @d.callbacks.query(pattern=r'absences-stats')
    async def absences_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        data: str = query.data.replace('absences-', '')

        if not data.endswith('-stats'):
            # Пока только за всё время
            keyboard: Keyboard = [[Button(_(f'buttons.stats.period.{arg}'), 
                                          callback_data=f'absences-{arg}-stats') for arg in ['all']]]
            await query.edit_message_text(_('texts.stats.period'), 
                                          parse_mode='MarkdownV2', 
                                          reply_markup=InlineKeyboardMarkup(keyboard))
            return
        

    def get_absences_stats_by_teacher(self, db, teacher_id: str) -> BytesIO:
        teacher: Teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == teacher_id))
        reasons = [ _(f'buttons.absences.fill.reason.{v}')[2] for v in ['excused', 'sick', 'cut'] ]
        school_dates: list = [ f'{d.day}' for d in teacher.school_days ] + [_('table.total')]
        
        indexes = pd.MultiIndex.from_product([school_dates, reasons], names=[_('table.indexes.date'), _('table.indexes.reason')])
        additional_cols: list = [
            (_('table.additional.general'), _('table.additional.count')),
            (_('table.additional.general'), _('table.additional.days'))
        ]
        columns = [
            (None, _('table.student'))
        ] + indexes.to_list() + additional_cols

        columns = pd.MultiIndex.from_tuples(columns)

        students = [ s.name for s in teacher.students ]
        df = pd.DataFrame({_('table.student'): students})
        empty_data = pd.DataFrame(index=range(len(students)),
                                  columns=columns[1:]
                                  )
        
        # TODO: заполнить пустые данными по кол-ву пропусков
        df = pd.concat([df, empty_data], axis=1)
        df.columns = columns

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Журнал')
        writer.close() 
        output.seek(0) 

        return output

        
        
    @d.callbacks.query(pattern=r'absences-all-stats')
    async def absences_stats_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        with self._get_session(context.application) as s:
            excel_file = self.get_absences_stats_by_teacher(s, update.effective_user.id)
            

            await query.edit_message_text(_('texts.stats.success_by', start='1', end='2'),
                                          parse_mode='MarkdownV2')
            await context.bot.send_document(
                update.effective_chat.id, 
                document=excel_file,
                filename='журнал-учета.xlsx'
            )