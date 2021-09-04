from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
import logging


from manager import Manager
from schedule import Schedule
from db import ActiveUser

import info # personal information

KEY: str = info.KEY # bot token

ADMINS: list = info.ADMINS # list of telegram ids here

logging.basicConfig(level = logging.DEBUG)



class BotState:
    REGISTER = 0
    IDLE = 1

class Keyboard:
    def __init__(self):
        self.IDLE_KEYBOARD = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.SCHEDULE_KEYBOARD = types.InlineKeyboardMarkup(row_width=2)

        self.IDLE_KEYBOARD.row(
            types.KeyboardButton(text="Сегодня"),
            types.KeyboardButton(text="Завтра")
        )
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text="Расписание"))
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text="Сейчас"))
        # self.IDLE_KEYBOARD.add(types.KeyboardButton(text="Где?"))
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text="Выйти"))

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Понедельник :arrow_up:"), callback_data="01"),
            types.InlineKeyboardButton(emojize("Понедельник :arrow_down:"), callback_data="00")
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Вторник :arrow_up:"), callback_data="11"),
            types.InlineKeyboardButton(emojize("Вторник :arrow_down:"), callback_data="10")
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Среда :arrow_up:"), callback_data="21"),
            types.InlineKeyboardButton(emojize("Среда :arrow_down:"), callback_data="20")
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Четверг :arrow_up:"), callback_data="31"),
            types.InlineKeyboardButton(emojize("Четверг :arrow_down:"), callback_data="30")
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Пятница :arrow_up:"), callback_data="41"),
            types.InlineKeyboardButton(emojize("Пятница :arrow_down:"), callback_data="40")
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(emojize("Суббота :arrow_up:"), callback_data="51"),
            types.InlineKeyboardButton(emojize("Суббота :arrow_down:"), callback_data="50")
        )

        self.SCHEDULE_KEYBOARD.add(
            types.InlineKeyboardButton("Время", callback_data="99")
        )

        self.SCHEDULE_KEYBOARD.add(
            types.InlineKeyboardButton("Неделя", callback_data="88")
        )



bot = Bot(token=KEY)
dp = Dispatcher(bot)
manager = Manager("sqlite:///lessons.db")
schedule = Schedule()

keyboard = Keyboard()

async def add_user_critical(user_id):
    manager.add_user(user_id)
    await bot.send_message(user_id, "Простите, похоже что-то случилось с базой данных.\nУкажите пожалуйста свою группу. Для этого просто отправте её номер в сообщении.")

@dp.message_handler(commands=["help"])
async def help_handler(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Nothing here yet")

@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    user_id = msg.from_user.id
    data = manager.get_user(user_id)
    if data is not None and data[1] is not None:
        await bot.send_message(msg.from_user.id, f"Снова здравствуйте!\nВаша группа: {data[1].group}", reply_markup=keyboard.IDLE_KEYBOARD)
    else:
        if data is None:
            manager.add_user(user_id)
        await bot.send_message(msg.from_user.id, f"Добро пожаловать!\nВведите номер вашей группы")

@dp.message_handler(lambda msg: msg.text.lower() == "сегодня")
async def today_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            sch = schedule.today(user_group.group)
            if len(sch) == 0:
                await bot.send_message(user_id, "Сегодня у вас нет пар ;)")
            else:
                await bot.send_message(user_id, "\n\n".join(sch))
        else:
            await bot.send_message(user_id, "Вы ещё не указали свою группу!")

@dp.message_handler(lambda msg: msg.text.lower() == "завтра")
async def tomorrow_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            sch = schedule.tomorrow(user_group.group)
            if (len(sch) == 0):
                await bot.send_message(user_id, "Завтра у вас нет пар\nПовезло повезло")
            else:
                await bot.send_message(user_id, "\n\n".join(sch))
        else:
            await bot.send_message(user_id, "Вы ещё не указали свою группу!")

@dp.message_handler(lambda msg: msg.text.lower() == "сейчас")
async def now_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            now = schedule.now(user_group.group)
            await bot.send_message(user_id, now)
        else:
            await bot.send_message(user_id, "Вы ещё не указали свою группу!")


@dp.message_handler(lambda msg: msg.text.lower() == "расписание")
async def schedule_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            await bot.send_message(user_id, "Какое расписание вам нужно?", reply_markup=keyboard.SCHEDULE_KEYBOARD)

@dp.message_handler(lambda msg: msg.text.lower() == "выйти")
async def quit_handler(msg: types.Message):
    user_id = msg.from_user.id
    manager.logout_user(user_id)
    await bot.send_message(user_id, "Хорошо, теперь вы можете указать другую группу.\nПросто напишите её в сообщении", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda msg: msg.text.lower().startswith("рассылка:"))
async def masssend_handler(msg: types.Message):
    user_id = msg.from_user.id
    if user_id in ADMINS:
        text = msg.text[10:]
        all_users = manager.get_all_users()
        for user in all_users:
            await bot.send_message(user.tid, text)
        await bot.send_message(user_id, "ok!")
            
    

@dp.message_handler()
async def message_handler(msg: types.Message):
    user_id = msg.from_user.id
    state = manager.get_user_state(user_id)
    print("STATE:", state)
    if state == BotState.REGISTER:
        group = msg.text
        ok = manager.group_exists(group)
        if ok:
            manager.login_user(user_id, group, BotState.IDLE)
            await bot.send_message(user_id, f"Ок!\nТеперь ваша группа: {group}", reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await bot.send_message(user_id, "Не получается найти группу с таким именем :(")


@dp.callback_query_handler()
async def process_schedule(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    d, l = int(callback.data[0]), int(callback.data[1])
    user_id = callback.from_user.id
    if d == 9:
        await bot.send_message(user_id, schedule.time_schedule())
    elif d == 8:
        await bot.send_message(user_id, f"Сейчас неделя {'над' if schedule.is_overline() else 'под'} чертой")
    else:
        user_info: ActiveUser
        data = manager.get_user(user_id)
        if data is None:
            add_user_critical(user_id)
        else:
            user_info, user_group = data
            if user_info.state == BotState.IDLE and user_group is not None:
                sch = schedule.day_schedule(user_group.group, d, bool(l))
                if len(sch) == 0:
                    await bot.send_message(user_id, "В этот день у вас нет пар")
                else:
                    await bot.send_message(user_id, "\n\n".join(sch))
            else:
                await bot.send_message(user_id, "Вы ещё не указали свою группу!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
