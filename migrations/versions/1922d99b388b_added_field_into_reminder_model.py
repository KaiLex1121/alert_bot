"""Added field into Reminder model

Revision ID: 1922d99b388b
Revises: 1f0dd7db3e7a
Create Date: 2025-04-29 22:49:56.235425

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1922d99b388b"
down_revision: Union[str, None] = "1f0dd7db3e7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавляем server_default=func.now() к столбцу start_datetime
    op.alter_column(
        table_name="reminders",
        column_name="start_datetime",
        server_default=sa.func.now(),
    )
    # Опционально: если столбец был nullable, делаем его NOT NULL
    op.alter_column(
        table_name="reminders", column_name="start_datetime", nullable=False
    )
    # Опционально: обновляем существующие записи, если start_datetime NULL
    op.execute(
        "UPDATE reminders SET start_datetime = NOW() WHERE start_datetime IS NULL"
    )


def downgrade():
    # Удаляем server_default и возвращаем столбец к предыдущему состоянию
    op.alter_column(
        table_name="reminders", column_name="start_datetime", server_default=None
    )
    # Возвращаем nullable=True, если это было в предыдущей версии
    op.alter_column(table_name="reminders", column_name="start_datetime", nullable=True)
