from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from misc import dp, bot
from states import Common, GroupAdmin, NewGroup, NewProfile, GroupsList
from database import db
from config.config import admin_id
from aiogram.utils.callback_data import CallbackData
import random, string


m_group = CallbackData("group", "group_id")
new_profile = CallbackData("profile", "group_id")


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    chat_id = message.from_user.id
    user = await db.User.get(chat_id)
    if not user:
        user = db.User()
        user.id = chat_id
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
        user.nickname = message.from_user.username
        await user.create()
    group_link_id = message.get_args()
    print(group_link_id)
    text = (
        f"Добро пожаловать, {user.first_name} в тайного санту \n"
        + "Для работы с ботом напиши команду /menu \n"
    )
    if group_link_id:
        group = await db.Group.query.where(db.Group.link == group_link_id).gino.first()
        if not group:
            await message.answer(text=text)
            return
        profile = await db.Profile.query.where(
            db.Profile.user_id == user.id and db.Profile.group_id == group.id
        ).gino.first()
        text = [
            f"Добро пожаловать, {user.first_name} в тайного санту \n",
            f"Ты прошел по ссылке в группу {group.name}! \n",
            "Для участия тебе надо будет заполнить анкету",
            "Продолжить ?",
        ]
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Да", callback_data=new_profile.new(group_id=group.id)
                    )
                ],
                [InlineKeyboardButton(text="Нет", callback_data="cancel")],
            ]
        )

        await message.answer(text="\n".join(text), reply_markup=markup)
        await NewProfile.Begin.set()

    else:
        await message.answer(text=text)


@dp.callback_query_handler(text="cancel", state=NewProfile)
async def cancel_profile(call: types.CallbackQuery, state: FSMContext):
    text = "Вы отменили заполнение анкеты !\n Для работы с ботом воспользуйся коммандой /menu"

    await call.message.edit_reply_markup()
    await call.message.answer(text=text)
    await state.reset_state()


@dp.callback_query_handler(new_profile.filter(), state=NewProfile.Begin)
async def create_profile(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    await call.message.edit_reply_markup()
    group_id = callback_data.get("group_id")
    profile = db.Profile()
    profile.user_id = call.from_user.id

    await call.message.answer(
        text="Введи свой вишлист (ты сможешь подправить его до жеребьевки)"
    )
    await NewProfile.EnterWish.set()
    await state.set_data(profile=profile)


@dp.message_handler(state=NewProfile.EnterWish, content_types=types.ContentTypes.TEXT)
async def enter_wish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    profile: db.Profile = data.get("profile")
    profile.wishlist = message.text

    await message.answer(text="Теперь введи то, что ты не хочешь получить")
    await NewProfile.EnterUnwish.set()
    await state.update_data(profile=profile)


@dp.message_handler(state=NewProfile.EnterUnwish, content_types=types.ContentTypes.TEXT)
async def enter_unwish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    profile: db.Profile = data.get("profile")
    profile.unwishlist = message.text

    await message.answer(
        text="Теперь введи ник (начинается с @) человека которому ты не хочешь/не можешь/не должен дарить подарок\n Если таких нет напиши <i>Никто</i>"
    )
    await NewProfile.EnterInvalidUserName.set()
    await state.update_data(profile=profile)


@dp.message_handler(
    state=NewProfile.EnterInvalidUserName, content_types=types.ContentTypes.TEXT
)
async def enter_unwish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    profile: db.Profile = data.get("profile")
    invalid_username = message.text.replace("@", "")
    if invalid_username.lower() != "никто":
        profile.invalid_username = invalid_username

    await profile.create()
    text = [
        "Твоя анкета сохранена",
        f"<b>Ты хочешь:</b> \n {profile.wishlist} \n",
        f"<b>Ты не хочешь:</b> \n {profile.unwishlist} \n",
        f"<b>Твоим сантой не может быть:</b> \n @{profile.invalid_username} \n"
        f"Для дальнейшей работы воспользуйся командой  /menu",
    ]

    await message.answer(text="\n".join(text))
    await state.reset_state()


@dp.message_handler(commands=["menu"], state="*")
async def cmd_groups(message: types.Message, state: FSMContext):
    (text, markup) = get_menu()
    await message.answer(text, reply_markup=markup)
    await state.reset_data()
    await Common.Menu.set()


@dp.callback_query_handler(text="groups", state=Common.Menu)
async def get_groups(call: types.CallbackQuery):
    groups = await db.Group.query.where(
        db.Group.admin_id == call.from_user.id
    ).gino.all()
    if not groups:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Создать группу", callback_data="newgroup")],
            ]
        )
        await call.message.edit_text(
            text="Вы не являетесь администратором ни одной группы", reply_markup=markup
        )
        await GroupsList.List.set()
    else:
        keys = list()
        keys.append([InlineKeyboardButton(text="Назад", callback_data="back")])
        for group in groups:
            group: db.Group
            keys.append(
                [
                    InlineKeyboardButton(
                        text=group.name,
                        callback_data=m_group.new(group_id=group.id),
                    )
                ]
            )
        keys.append(
            [InlineKeyboardButton(text="Создать группу", callback_data="newgroup")]
        )
        markup = InlineKeyboardMarkup(inline_keyboard=keys)
        text = "Выберите группу:"
        await call.message.answer(text, reply_markup=markup)
        await GroupsList.List.set()


@dp.callback_query_handler(text="newgroup", state=GroupsList.List)
async def create_group(call: types.CallbackQuery, state: FSMContext):
    group = db.Group()
    group.admin_id = call.from_user.id

    await call.message.edit_reply_markup()
    await call.message.answer(text="Введи название группы")
    await NewGroup.EnterName.set()
    await state.update_data(group=group.to_dict())


@dp.message_handler(state=NewGroup.EnterName, content_types=types.ContentTypes.TEXT)
async def enter_group_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data, state)
    group: db.Group = db.Group().from_dict(data.get("group"))
    group.name = message.text

    await message.answer(text="Введи описание группы")
    await NewGroup.EnterDescription.set()
    await state.update_data(group=group.to_dict())


@dp.message_handler(
    state=NewGroup.EnterDescription, content_types=types.ContentTypes.TEXT
)
async def enter_group_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group: db.Group = db.Group().from_dict(data.get("group"))
    group.description = message.text
    group.link = randomword(10)
    await group.create()
    invite_link = await get_bot_link(group_link_id=group.link)
    text = [
        "Отлично, группа создана",
        f"<b>Имя:</b> \n {group.name} \n",
        f"<b>Описание:</b> \n {group.description} \n"
        f"<b>Ссылка для приглашения друзей: </b> \n {invite_link} \n",
    ]

    await message.answer(text="\n".join(text))
    await state.reset_state()


@dp.callback_query_handler(m_group.filter())
async def manage_group(
    call: types.CallbackQuery, callback_data: dict, state: FSMContext
):
    group_id = int(callback_data.get("group_id"))
    await call.message.edit_reply_markup()

    group = await db.Group.get(group_id)
    if not group:
        await call.message.answer("Такой группы не существует")
        return

    profiles = (
        await db.Profile.load(user=db.User)
        .query.where(db.Profile.group_id == group_id)
        .gino.all()
    )
    profile_names = map(lambda x: f"<b>{x.user.name}</b>")
    bot_link = await get_bot_link(group.group_link_id)
    text = [
        f'Вы в режиме редактированния группы "<b>{group.name}</b>"',
        "Список участников: \n",
        "\n".join(profile_names),
        "Ссылка для регистрации:",
        bot_link,
        "\nВыберите действие:",
    ]

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back")],
            [
                InlineKeyboardButton(
                    text="Удалить участника", callback_data="remove profile"
                )
            ],
            [InlineKeyboardButton(text="Провести жеребьевку", callback_data="run")],
            [InlineKeyboardButton(text="! Удалить группу !", callback_data="delete")],
        ]
    )

    await call.message.edit_text(text="\n".join(text), reply_markup=markup)
    await GroupAdmin.Edit.set()
    await state.update_data(group=group)


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    if message.from_user.id == int(admin_id):
        commands = [
            types.BotCommand(command="/menu", description="Открыть меню"),
        ]
        await bot.set_my_commands(commands)
        await message.answer("Команды настроены.")


# Возвращается данны для отображения меню
def get_menu():
    text = "Воспользуйтесь меню для навигации"
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Мои группы (администрирование)", callback_data="groups"
                )
            ],
            [InlineKeyboardButton(text="Мои анкеты", callback_data="profiles")],
        ]
    )

    return (text, markup)


async def get_bot_link(group_link_id):
    bot_name = (await bot.me).username
    return f"https://t.me/{bot_name}?start={group_link_id}"


def randomword(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))
