from sqlalchemy import select
from telegram import (
    Update
)
from telegram.ext import (
    ContextTypes,
    Application
)
from app.bot.markly.models import Teacher
from app.bot.students.models import Student
from app.bot import messages as msg
from app.bot.utils.callbacks import Base
from app.bot.utils import decorators as d

class StudentCallback(Base):

    model = Student

    @d.callbacks.command(command='my_students')
    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_markdown("test work")

    @d.callbacks.query(pattern = r'student_add_')
    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        args = context.args
        if len(args) == 0:
            await update.message.reply_markdown(msg.NEED_STUDENTS)
            return
        
        with self._get_session(context.application) as db:
            teacher = db.scalar(select(Teacher).where(Teacher.telegram_id == update.effective_user.id))
            if teacher:
                for name in args:
                    student = self.model(teacher_id=teacher.id, name=name)
                    db.add(student)
                await update.message.reply_markdown(msg.FILL_STUDENTS_OK)
            else:
                await update.message.reply_markdown(msg.NO_REGISTRY_ERROR)
                return
    
    @d.callbacks.query(pattern=r'student_edit_')
    async def edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass

    @d.callbacks.query(pattern=r'student_delete_')
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass

    @d.callbacks.query(pattern=r'student_update_')
    async def update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        pass
