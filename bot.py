from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
import logging
import aioschedule
import asyncio
import textwrap
import base64
import argparse
import shlex

from manager import Manager
from schedule import Schedule
from db import ActiveUser
from times import Times
import weather

import info # personal information

KEY: str = info.KEY # bot token
ADMINS: list = info.ADMINS # list of telegram ids here
DB_USER: str = info.DB_USER
DB_PASS: str = info.DB_PASS
VIP: list = info.VIP

logging.basicConfig(level = logging.DEBUG)

class BotState:
    REGISTER = 0
    IDLE = 1

class Keyboard:
    def __init__(self):
        self.IDLE_KEYBOARD = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.SCHEDULE_KEYBOARD = types.InlineKeyboardMarkup(row_width=2)
        self.BACK_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
        self.GROUP_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)

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

        self.BACK_KEYBOARD.add(
            types.InlineKeyboardButton("Назад", callback_data="back")
        )

        self.GROUP_KEYBOARD.add(
            types.InlineKeyboardButton("Список групп", callback_data="grouplist")
        )

bot = Bot(token=KEY)
dp = Dispatcher(bot)
db = f"mysql://{DB_USER}:{DB_PASS}@localhost:3306/schedule?charset=utf8mb4"
manager = Manager(db)
schedule = Schedule(manager)

keyboard = Keyboard()

mailing_parser = argparse.ArgumentParser(exit_on_error=False)
mailing_parser.add_argument("-a", "--all", action="store_true", default=False)
mailing_parser.add_argument("-g", "--groups", 
                            action="extend", 
                            dest="groups", 
                            nargs="+",
                            type=str)
mailing_parser.add_argument("-m", "--message", action="store", type=str)


async def morning_greeting():
    message_template = textwrap.dedent("""\
    Доброе утро! Сегодня {date}, {weekday}.
    {weather}
    {header}
    {schedule}
    
    {end}
    """)
    today_weather = await weather.get_weather(location=296181)

    user_info: ActiveUser
    for vip_user in VIP:
        data = manager.get_user(vip_user)
        if data is not None:
            user_info, user_group = data
            if user_group is not None:
                sch = schedule.today(user_group.group)
                message = message_template.format(
                    weekday = Times.today_weekday().lower(),
                    date = Times.today_date(),
                    header = "Сегодня у вас нет пар" if len(sch) == 0 else "Ваше расписание на сегодня:",
                    weather = today_weather if today_weather is not None else "",
                    schedule = "Отдохните хорошенько!" if len(sch) == 0 else "\n\n".join(sch),
                    end = "Хорошего дня!"
                    )
                await bot.send_message(vip_user, emojize(message), reply_markup=keyboard.IDLE_KEYBOARD)
                

async def add_user_critical(user_id: int):
    manager.add_user(user_id)
    await bot.send_message(user_id, "Простите, похоже что-то случилось с базой данных.\nУкажите пожалуйста свою группу. Для этого просто отправте её номер в сообщении.")

async def not_logged_in_yet(user_id: int):
    await bot.send_message(user_id, "Вы ещё не указали свою группу!", reply_markup=keyboard.GROUP_KEYBOARD)


@dp.message_handler(commands=["help"])
async def help_handler(msg: types.Message):
    await bot.send_message(msg.from_user.id, "Nothing here yet")

@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    user_id = msg.from_user.id
    data = manager.get_user(user_id)
    args = msg.get_args()
    if args:
        group = base64.b64decode(args.encode("utf-8")).decode("utf-8")
        ok = manager.group_exists(group)
        if ok:
            manager.login_user(user_id, group, BotState.IDLE)
            await bot.send_message(user_id, f"Вы перешли по пригласительной ссылке.\nТеперь ваша группа: {group}", reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await bot.send_message(user_id, "С пригласительной ссылкой что-то не так!\nНо не переживайте, вы можете ввести интересующую вас группу самостоятельно, просто отправте её сообщением", reply_markup=keyboard.GROUP_KEYBOARD)
    else:
        if data is not None and data[1] is not None:
            await bot.send_message(msg.from_user.id, f"Снова здравствуйте!\nВаша группа: {data[1].group}", reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            if data is None:
                manager.add_user(user_id)
            await bot.send_message(msg.from_user.id, f"Добро пожаловать!\nВведите номер вашей группы", reply_markup=keyboard.GROUP_KEYBOARD)

@dp.message_handler(commands=["invite"])
async def invite_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            group: str = user_group.group
            group_base64 = base64.b64encode(group.encode("utf-8"))
            invite_link = f"https://t.me/istu_sc_bot?start={group_base64.decode('utf-8')}"
            await bot.send_message(user_id, invite_link, reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await not_logged_in_yet(user_id)


@dp.message_handler(commands=["today"])
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
            message_top = f"{Times.today_weekday()}. {'Над' if schedule.is_overline() else 'Под'} чертой.\n\n"
            if len(sch) == 0:
                await bot.send_message(user_id, message_top + "Сегодня у вас нет пар ;)", reply_markup=keyboard.IDLE_KEYBOARD)
            else:
                await bot.send_message(user_id, message_top + "\n\n".join(sch), reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await not_logged_in_yet(user_id)

@dp.message_handler(commands=["tomorrow"])
@dp.message_handler(lambda msg: msg.text.lower() == "завтра")
async def tomorrow_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            sch = schedule.tomorrow(user_group.group)
            message_top = f"{Times.tomorrow_weekday()}. {'Над' if schedule.is_overline(add=1) else 'Под'} чертой.\n\n"
            if (len(sch) == 0):
                await bot.send_message(
                    user_id, 
                    message_top + "Завтра у вас нет пар\nПовезло повезло", 
                    reply_markup=keyboard.IDLE_KEYBOARD
                    )
            else:
                await bot.send_message(
                    user_id, 
                    message_top + "\n\n".join(sch), 
                    reply_markup=keyboard.IDLE_KEYBOARD
                    )
        else:
            await not_logged_in_yet(user_id)

@dp.message_handler(commands=["now"])
@dp.message_handler(lambda msg: msg.text.lower() == "сейчас")
async def now_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            now = schedule.now(user_group.group)
            await bot.send_message(user_id, now, reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await not_logged_in_yet(user_id)


@dp.message_handler(commands=["schedule"])
@dp.message_handler(lambda msg: msg.text.lower() == "расписание")
async def schedule_handler(msg: types.Message):
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        if user_info.state == BotState.IDLE and user_group is not None:
            await bot.send_message(user_id, "Какое расписание вам нужно?", reply_markup=keyboard.SCHEDULE_KEYBOARD)
        else:
            await not_logged_in_yet(user_id)

@dp.message_handler(commands=["logout"])
@dp.message_handler(lambda msg: msg.text.lower() == "выйти")
async def quit_handler(msg: types.Message):
    user_id = msg.from_user.id
    manager.logout_user(user_id)
    await bot.send_message(user_id, "Хорошо, теперь вы можете указать другую группу.\nПросто напишите её в сообщении", reply_markup=types.ReplyKeyboardRemove())

# TODO make the newsletter more flexible
@dp.message_handler(lambda msg: msg.text.lower().startswith("рассылка:"))
async def masssend_handler(msg: types.Message):
    user_id = msg.from_user.id
    if user_id in ADMINS:
        text = msg.text[10:]
        all_users = manager.get_all_users()
        for user in all_users:
            await bot.send_message(user.tid, text)
        await bot.send_message(user_id, "ok!", reply_markup=keyboard.IDLE_KEYBOARD)

@dp.message_handler(commands=["mailing"]) # v2
async def mailing_handler(msg: types.Message):
    user_id = msg.from_user.id
    if user_id in ADMINS:
        message_args = msg.get_args()
        try:
            args = mailing_parser.parse_args(shlex.split(message_args))
        except Exception as error:
            await msg.reply("error!\n\n" + str(error), reply_markup=keyboard.IDLE_KEYBOARD)
            return
        for_all = args.all
        groups = args.groups
        message = args.message
        if for_all:
            all_users = manager.get_all_users()
            for user in all_users:
                await bot.send_message(user.tid, message)
            await msg.reply(f"ok!\nотправлено пользователям: {len(all_users)}", reply_markup=keyboard.IDLE_KEYBOARD)
        elif groups is not None and len(groups) > 0:
            users = manager.get_users_in_groups(groups)
            for user in users:
                await bot.send_message(user.tid, message)
            await msg.reply(f"ok!\nотправлено пользователям: {len(users)}", reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await msg.reply(
                f"Не указаны фильтры для отправки. Чтобы отправить сообщение всем, испольуйте ключ -a или --all",
                reply_markup=keyboard.IDLE_KEYBOARD
            )



@dp.message_handler()
async def message_handler(msg: types.Message):
    user_id = msg.from_user.id
    state = manager.get_user_state(user_id)
    if state == BotState.REGISTER:
        group = msg.text
        ok = manager.group_exists(group)
        if ok:
            manager.login_user(user_id, group, BotState.IDLE)
            await bot.send_message(user_id, f"Ок!\nТеперь ваша группа: {group}", reply_markup=keyboard.IDLE_KEYBOARD)
        else:
            await bot.send_message(user_id, "Не получается найти группу с таким именем :(", reply_markup=keyboard.GROUP_KEYBOARD)

@dp.callback_query_handler(lambda c: c.data == "back")
async def inline_back(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        "Какое расписание вам нужно?", 
        chat_id = callback.from_user.id,
        message_id = callback.message.message_id,
        reply_markup=keyboard.SCHEDULE_KEYBOARD
        )
    
@dp.callback_query_handler(lambda c: c.data == "grouplist")
async def inline_group_list(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    groups = manager.get_groups()
    await bot.send_message(user_id, "Список групп:\n" + "\n".join([str(g) for g in sorted(groups, key=str)]))



@dp.callback_query_handler()
async def process_schedule(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    d, l = int(callback.data[0]), int(callback.data[1])
    user_id = callback.from_user.id
    message_id = callback.message.message_id
    if d == 9: # Time schedule
        await bot.edit_message_text(
            schedule.time_schedule(),
            chat_id=user_id,
            message_id=message_id,
            reply_markup=keyboard.BACK_KEYBOARD
            )
        # await bot.send_message(user_id, schedule.time_schedule(), reply_markup=keyboard.IDLE_KEYBOARD)
    elif d == 8: # Is week underline
        await bot.edit_message_text(
           f"Сейчас неделя {'над' if schedule.is_overline() else 'под'} чертой", 
           chat_id=user_id,
           message_id=message_id,
           reply_markup=keyboard.BACK_KEYBOARD     
        )
    else:
        user_info: ActiveUser
        data = manager.get_user(user_id)
        if data is None:
            await add_user_critical(user_id)
        else:
            user_info, user_group = data
            if user_info.state == BotState.IDLE and user_group is not None:
                sch = schedule.day_schedule(user_group.group, d, bool(l))
                message_top = f"{Times.weekdays[d]}. {'Над' if bool(l) else 'Под'} чертой.\n\n"
                if len(sch) == 0:
                    await bot.edit_message_text(
                        message_top + "В этот день у вас нет пар",
                        chat_id=user_id,
                        message_id=message_id, 
                        reply_markup=keyboard.BACK_KEYBOARD
                    )
                else:
                    await bot.edit_message_text(
                        message_top + "\n\n".join(sch),
                        chat_id=user_id,
                        message_id=message_id, 
                        reply_markup=keyboard.BACK_KEYBOARD
                    )
                    #await bot.send_message(user_id, "\n\n".join(sch), reply_markup=keyboard.IDLE_KEYBOARD)
            else:
                # await bot.send_message(user_id, "Вы ещё не указали свою группу!")
                await bot.edit_message_text(
                    "Вы ещё не указали свою группу!",
                    chat_id=user_id,
                    message_id=message_id,
                    reply_markup=keyboard.IDLE_KEYBOARD
                )

async def morning_scheduler():
    aioschedule.every().day.at("8:00").do(morning_greeting)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)

async def setup(_):
    asyncio.create_task(morning_scheduler())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=setup)
