from sqlalchemy import BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column

# from app.models import dto
from src.database.models.base import Base
from src.enums.general import TypeOfChat


class Chat(Base):
    __tablename__ = "chats"
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    type: Mapped[TypeOfChat] = mapped_column(Enum(TypeOfChat))
    title: Mapped[str]
    username: Mapped[str | None]

    def __repr__(self):
        rez = f"<Chat " f"ID={self.tg_id} " f"title={self.title} "
        if self.username:
            rez += f"username=@{self.username}"
        return rez + ">"


#     # def to_dto(self) -> dto.Chat:
#     #     return dto.Chat(
#     #         db_id=self.id,
#     #         tg_id=self.tg_id,
#     #         type=self.type,
#     #         title=self.title,
#     #         username=self.username,
#     #     )
