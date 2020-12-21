from aiogram import types, Bot
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Sequence,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    TEXT,
)
from sqlalchemy import sql

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    nickname = Column(String(100), nullable=False)
    created_at = Column(DateTime(), server_default=sql.func.now())

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username
        )


PROFILE_ID = Sequence("profiles_id_seq", start=1, increment=1)


class Profile(db.Model):
    __tablename__ = "profiles"
    query: sql.Select

    id = Column(
        Integer,
        PROFILE_ID,
        primary_key=True,
        server_default=PROFILE_ID.next_value(),
        autoincrement=True,
    )
    user_id = Column(BigInteger, ForeignKey("users.id"))
    wishlist = Column(TEXT)
    unwishlist = Column(TEXT)
    invalid_username = Column(String(100))
    created_at = Column(DateTime(), server_default=sql.func.now())
    _invalid: User = None

    @property
    def invalid(self):
        return self._invalid

    @invalid.setter
    def invalid(self, value: User):
        self._invalid = value


GROUP_ID = Sequence("groups_id_seq", start=1, increment=1)


class Group(db.Model):
    __tablename__ = "groups"
    query: sql.Select

    id = Column(
        Integer,
        GROUP_ID,
        primary_key=True,
        server_default=GROUP_ID.next_value(),
        autoincrement=True,
    )
    name = Column(String(100), nullable=False)
    description = Column(TEXT)
    link = Column(String(10), nullable=False)
    admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(), server_default=sql.func.now())
    is_finished = Column(Boolean, default=False)
    _admin: User = None

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, value):
        self._admin = value

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "link": self.link,
            "admin_id": self.admin_id,
            "created_at": self.created_at,
            "is_finished": self.is_finished,
        }

    def from_dict(self, d: dict):
        self.name = d.get("name")
        self.description = d.get("description")
        self.link = d.get("link")
        self.admin_id = d.get("admin_id")
        self.created_at = d.get("created_at")
        self.is_finished = d.get("is_finished")

        return self


PAIR_ID = Sequence("pairs_id_seq", start=1, increment=1)


class Pair(db.Model):
    __tablename__ = "pairs"
    query: sql.Select

    id = Column(
        Integer,
        PAIR_ID,
        primary_key=True,
        server_default=PAIR_ID.next_value(),
        autoincrement=True,
    )
    giver_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    reciever_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(DateTime(), server_default=sql.func.now())
    _group: Group = None
    _giver: User = None
    _reciever: User = None

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value: Group):
        self._group = value

    @property
    def giver(self):
        return self._giver

    @giver.setter
    def giver(self, value: User):
        self._giver = value

    @property
    def reciever(self):
        return self._reciever

    @reciever.setter
    def reciever(self, value: User):
        self._reciever = value


async def create_db(db_user: String, db_pass: String, host: String):
    await db.set_bind(f"postgresql://{db_user}:{db_pass}@{host}/gino")

    # Create tables - выполняем один раз при первом запуске
    db.gino: GinoSchemaVisitor
    # await db.gino.create_all()