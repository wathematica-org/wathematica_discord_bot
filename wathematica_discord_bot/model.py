import datetime
import enum
from typing import Optional

from sqlalchemy import ForeignKey
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


# table definition
# for guild
class Guild(Base):
    __tablename__ = "guild"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    guild_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]

    interesting_emoji_id: Mapped[Optional[int]] = mapped_column(default=None)
    role_setting_channel_id: Mapped[Optional[int]] = mapped_column(default=None)
    system_channel_id: Mapped[Optional[int]] = mapped_column(default=None)
    engineer_role_id: Mapped[Optional[int]] = mapped_column(default=None)


# for category
class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    category_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]

    guild_id: Mapped[int] = mapped_column(ForeignKey("guild.guild_id"))
    state: Mapped[SeminarState]
    category_type: Mapped[str] = mapped_column(default="regular")


# for seminar
class Seminar(Base):
    __tablename__ = "seminar"

    # id will be automatically assigned by the database, so it should not be initialized in the constructor
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"))

    name: Mapped[str]
    created_at: Mapped[datetime.datetime]
    finished_at: Mapped[Optional[datetime.datetime]]
    leader_id: Mapped[int]

    channel_id: Mapped[int] = mapped_column(unique=True)
    role_id: Mapped[int] = mapped_column(unique=True)
    role_setting_message_id: Mapped[int] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    # Enum type can be directly mapped to SQLAlchemy Column type.
    # See https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-python-enum-or-pep-586-literal-types-in-the-type-map for more details
