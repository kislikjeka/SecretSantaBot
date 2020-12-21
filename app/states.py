from aiogram.dispatcher.filters.state import StatesGroup, State


class Common(StatesGroup):
    Menu = State()


class NewGroup(StatesGroup):
    EnterName = State()
    EnterDescription = State()


class GroupsList(StatesGroup):
    List = State()


class GroupAdmin(StatesGroup):
    Edit = State()
    UpdateName = State()
    Confirm = State()


class NewProfile(StatesGroup):
    Begin = State()
    EnterWish = State()
    EnterUnwish = State()
    EnterInvalidUserName = State()
    Confirm = State()


class EditProfile(StatesGroup):
    Begin = State()
