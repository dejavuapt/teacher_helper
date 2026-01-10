from app.bot.utils.callbacks import Base
from app.bot.modules.absences.models import Absence, SchoolDay, Teacher
from app.bot.utils import decorators as d
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
)
from sqlalchemy import select
from app.bot.utils.types import Keyboard, Button
from app.bot.locales import get_text as _
import pandas as pd
import numpy as np
from io import BytesIO
import datetime


class StatisticsCallbacks(Base):

    @d.callbacks.query(pattern=r"absences-stats")
    async def absences_stats(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        await query.answer()

        data: str = query.data.replace("absences-", "")

        if not data.endswith("-stats"):
            # Пока только за всё время
            keyboard: Keyboard = [
                [
                    Button(
                        _(f"buttons.stats.period.{arg}"),
                        callback_data=f"absences-{arg}-stats",
                    )
                    for arg in ["all"]
                ]
            ]
            await query.edit_message_text(
                _("texts.stats.period"),
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

    def get_absences_stats_by_teacher(self, session, teacher_id: str) -> BytesIO:
        teacher: Teacher = session.scalar(
            select(Teacher).where(Teacher.telegram_id == teacher_id)
        )

        map_reason = {
            v: _(f"buttons.absences.fill.reason.{v}")[2]
            for v in ["excused", "sick", "cut"]
        }
        school_dates: list = [d.day for d in teacher.school_days] + [_("table.total")]

        indexes = pd.MultiIndex.from_product(
            [school_dates, map_reason.values()],
            names=[_("table.indexes.date"), _("table.indexes.reason")],
        )
        columns = [(None, _("table.student"))] + indexes.to_list()
        columns = pd.MultiIndex.from_tuples(columns)

        students = [s.name for s in teacher.students]

        empty_data = pd.DataFrame(dtype=np.int16, index=students, columns=columns[1:])
        df = empty_data

        # TODO: Когда появится redis, то закэшировать генерацию данных
        for date, sub_df in df.groupby(level=0, axis=1):
            if not isinstance(date, datetime.date):
                break

            absences: list[Absence] = (
                session.execute(
                    select(Absence, SchoolDay)
                    .select_from(Absence)
                    .join(SchoolDay, Absence.schoolday_id == SchoolDay.id)
                    .where(SchoolDay.day == date)
                    .where(SchoolDay.teacher_id == teacher.id)
                )
                .scalars()
                .all()
            )

            for a in absences:
                r = map_reason.get(a.reason)
                row_idx = [a.student.name]
                col_idx = [[(_("table.total"), r)], [(date, r)]]

                df.loc[
                    row_idx,
                    col_idx[1],
                ] = a.number

        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Журнал")
        writer.close()
        output.seek(0)

        return output

    @d.callbacks.query(pattern=r"absences-all-stats")
    async def absences_stats_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        await query.answer()
        with self._get_session(context.application) as s:
            excel_file = self.get_absences_stats_by_teacher(s, update.effective_user.id)

            await query.edit_message_text(
                _("texts.stats.success_by_all", start="1", end="2"),
                parse_mode="MarkdownV2",
            )
            await context.bot.send_document(
                update.effective_chat.id,
                document=excel_file,
                filename="журнал-учета.xlsx",
            )
