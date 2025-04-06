from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models import Base
from .user import User

class Notification(Base):
    __tablename__ = "notifications"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            ondelete="CASCADE"
        )
    )
    user: Mapped['User'] = relationship(
        back_populates="advertisments",
        lazy="joined"
    )

    def __repr__(self):
        rez = (
            f"<User "
            f"ID={self.tg_id} "
            f"name={self.first_name} {self.last_name} "
        )
        if self.username:
            rez += f"username=@{self.username}"
        return rez + ">"
