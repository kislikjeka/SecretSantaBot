from aiogram import types, Bot
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Sequence,
    TIMESTAMP,
    Boolean,
    JSON,
    DATETIME,
    ForeignKey,
    TEXT,
)
from sqlalchemy import sql

from ..config.config import db_pass, db_user, host

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = Column(Integer, Sequence(user_id_seq), primary_key=True)
    user_id = Column(BigInteger)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    nickname = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username
        )


class Profile(db.Model):
    __tablename__ = "profiles"
    query: sql.Select

    id = Column(Integer, Sequence(profile_id_seq), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    wishlist = Column(TEXT)
    invalid_id = Column(Integer, ForeignKey("users.id"))
    _invalid: User = None

    @property
    def invalid(self):
        return self._invalid

    @invalid.setter
    def invalid(self, value: User):
        self._invalid = value


class Group(db.Model):
    __tablename__ = "groups"
    query: sql.Select

    id = Column(Integer, Sequence(group_id_seq), primary_key=True)
    name = Column(String(100), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    _admin: User = None

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, value):
        self._admin = value


class Pair(db.Model):
    __tablename__ = "pairs"
    query: sql.Select

    id = Column(Integer, Sequence(pairs_id_seq), primary_key=True)
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reciever_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
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