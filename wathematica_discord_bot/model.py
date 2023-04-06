import datetime
import enum
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class SeminarState(enum.Enum):
    # enum.auto() clarifies the fact that the value of the enum has no meaning
    PENDING = enum.auto()
    ONGOING = enum.auto()
    PAUSED = enum.auto()
    FINISHED = enum.auto()


class Base(DeclarativeBase, MappedAsDataclass):
    # Base.metadata will store the information of all the tables that inherit this class
    pass


# Table definition
class Seminar(Base):
    __tablename__ = "seminar"

    # id will be automatically assigned by the database, so it should not be initialized in the constructor
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    server_id: Mapped[int]
    name: Mapped[str]
    created_at: Mapped[datetime.datetime]
    finished_at: Mapped[Optional[datetime.datetime]]
    seminar_state: Mapped[SeminarState]
    leader_id: Mapped[int]
    channel_id: Mapped[int] = mapped_column(unique=True)
    role_id: Mapped[int] = mapped_column(unique=True)
    role_setting_message_id: Mapped[int] = mapped_column(unique=True)
    # Enum type can be directly mapped to SQLAlchemy Column type.
    # See https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-python-enum-or-pep-586-literal-types-in-the-type-map for more details
