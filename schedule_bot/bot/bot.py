import asyncio
import shlex
import textwrap
from typing import Any, List

import aioschedule
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.emoji import emojize
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from schedule_bot import (
    REDIS_HOST,
    REDIS_PORT,
    TELEGRAM_KEY
)
from schedule_bot import info
from schedule_bot.bot import config
from schedule_bot.bot.keyboard import Keyboard
from schedule_bot.bot.mailing import mailing_parser
from schedule_bot.db import ActiveUser
from schedule_bot.manager import manager
from schedule_bot.schedule import Schedule
from schedule_bot.utils import weather
from schedule_bot.utils.times import Times

KEY: str = TELEGRAM_KEY
ADMINS: List[int] = config['bot']['admins']
VIP: List[int] = info.VIP


class States(StatesGroup):
    REGISTER = State()
    IDLE = State()


redis = RedisStorage2(REDIS_HOST, REDIS_PORT)
bot = Bot(token=KEY)
dp = Dispatcher(bot, storage=redis)
schedule = Schedule()

keyboard = Keyboard()


async def morning_greeting() -> None:
    message_template = textwrap.dedent(
        """\
    Доброе утро! Сегодня {date}, {weekday}.
    {weather}
    {header}
    {schedule}

    {end}
    """
    )
    today_weather = await weather.get_weather(location=296181)

    user_info: ActiveUser
    for vip_user in VIP:
        data = manager.get_user(vip_user)
        if data is not None:
            user_info, user_group = data
            if user_group is not None:
                sch = schedule.today(user_group.group)
                message = message_template.format(
                    weekday=Times.today_weekday().lower(),
                    date=Times.today_date(),
                    header="Сегодня у вас нет пар"
                    if len(sch) == 0
                    else "Ваше расписание на сегодня:",
                    weather=today_weather if today_weather is not None else "",
                    schedule="Отдохните хорошенько!"
                    if len(sch) == 0
                    else "\n\n".join(sch),
                    end="Хорошего дня!",
                )
                await bot.send_message(
                    vip_user,
                    emojize(message),
                    reply_markup=keyboard.IDLE_KEYBOARD,
                )


async def add_user_critical(user_id: int) -> None:
    manager.add_user(user_id)
    await States.REGISTER.set()
    await bot.send_message(
        user_id,
        "Простите, похоже что-то случилось с базой данных.\nУкажите пожалуйста свою группу. Для этого просто отправте её номер в сообщении.",
    )


async def not_logged_in_yet(user_id: int) -> None:
    await bot.send_message(
        user_id,
        "Вы ещё не указали свою группу!",
        reply_markup=keyboard.GROUP_KEYBOARD,
    )


@dp.message_handler(commands=["help"], state='*')
async def help_handler(msg: types.Message) -> None:
    await bot.send_message(msg.from_user.id, "Nothing here yet")


@dp.message_handler(commands=["start"], state='*')
async def start_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    data = manager.get_user(user_id)
    args = msg.get_args()
    if args:  # invite link
        if data is None:
            manager.add_user(user_id)
        try:
            group = decode_payload(args)
            ok = manager.group_exists(group)
        except ValueError:
            ok = False
        if ok:
            manager.set_user_group(user_id, group)
            await States.IDLE.set()
            await bot.send_message(
                user_id,
                f"Вы перешли по пригласительной ссылке.\nТеперь ваша группа: {group}",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        else:
            await States.REGISTER.set()
            await bot.send_message(
                user_id,
                "С пригласительной ссылкой что-то не так!\nНо не переживайте, вы можете ввести интересующую вас группу самостоятельно, просто отправте её сообщением",
                reply_markup=keyboard.GROUP_KEYBOARD,
            )
    else:
        if data is not None and data[1] is not None:
            await States.IDLE.set()
            await bot.send_message(
                msg.from_user.id,
                f"Снова здравствуйте!\nВаша группа: {data[1].group}",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        else:
            if data is None:
                manager.add_user(user_id)
            await States.REGISTER.set()
            await bot.send_message(
                msg.from_user.id,
                "Добро пожаловать!\nВведите номер вашей группы",
                reply_markup=keyboard.GROUP_KEYBOARD,
            )


@dp.message_handler(commands=["invite"], state=States.IDLE)
async def invite_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        group: str = user_group.group
        invite_link = await get_start_link(payload=group, encode=True)
        await bot.send_message(
            user_id, invite_link, reply_markup=keyboard.IDLE_KEYBOARD
        )


@dp.message_handler(commands=['invite'], state=States.REGISTER)
async def invite_no_group_handler(msg: types.Message) -> None:
    await not_logged_in_yet(msg.from_user.id)


@dp.message_handler(commands=["today"], state=States.IDLE)
@dp.message_handler(
    lambda msg: msg.text.lower() == "сегодня", state=States.IDLE
)
async def today_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        sch = schedule.today(user_group.group)
        message_top = f"{Times.today_weekday()}. {'Над' if schedule.is_overline() else 'Под'} чертой.\n\n"
        if len(sch) == 0:
            await bot.send_message(
                user_id,
                message_top + "Сегодня у вас нет пар ;)",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        else:
            await bot.send_message(
                user_id,
                message_top + "\n\n".join(sch),
                reply_markup=keyboard.IDLE_KEYBOARD,
            )


@dp.message_handler(commands=["tomorrow"], state=States.IDLE)
@dp.message_handler(lambda msg: msg.text.lower() == "завтра", state=States.IDLE)
async def tomorrow_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        sch = schedule.tomorrow(user_group.group)
        message_top = f"{Times.tomorrow_weekday()}. {'Над' if schedule.is_overline(add=1) else 'Под'} чертой.\n\n"
        if len(sch) == 0:
            await bot.send_message(
                user_id,
                message_top + "Завтра у вас нет пар\nПовезло повезло",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        else:
            await bot.send_message(
                user_id,
                message_top + "\n\n".join(sch),
                reply_markup=keyboard.IDLE_KEYBOARD,
            )


@dp.message_handler(commands=["now"], state=States.IDLE)
@dp.message_handler(lambda msg: msg.text.lower() == "сейчас", state=States.IDLE)
async def now_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        now = schedule.now(user_info.group)
        await bot.send_message(
            user_id, now, reply_markup=keyboard.IDLE_KEYBOARD
        )


@dp.message_handler(commands=["schedule"], state=States.IDLE)
@dp.message_handler(
    lambda msg: msg.text.lower() == "расписание", state=States.IDLE
)
async def schedule_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    user_info: ActiveUser
    data = manager.get_user(user_id)
    if data is None:
        await add_user_critical(user_id)
    else:
        user_info, user_group = data
        await bot.send_message(
            user_id,
            "Какое расписание вам нужно?",
            reply_markup=keyboard.SCHEDULE_KEYBOARD,
        )


@dp.message_handler(commands=["week"], state='*')
async def week_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    await bot.send_message(
        user_id,
        f"Сейчас неделя {'над' if schedule.is_overline() else 'под'} чертой",
    )


@dp.message_handler(commands=["times"], state='*')
async def times_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    await bot.send_message(user_id, schedule.time_schedule())


@dp.message_handler(commands=["logout"], state='*')
@dp.message_handler(lambda msg: msg.text.lower() == "выйти", state='*')
async def quit_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    manager.drop_user_group(user_id)
    await States.REGISTER.set()
    await bot.send_message(
        user_id,
        "Хорошо, теперь вы можете указать другую группу.\nПросто напишите её в сообщении",
        reply_markup=types.ReplyKeyboardRemove(),
    )


# TODO make the newsletter more flexible
@dp.message_handler(lambda msg: msg.text.lower().startswith("рассылка:"))
async def masssend_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    if user_id in ADMINS:
        text = msg.text[10:]
        all_users = manager.get_all_users()
        for user in all_users:
            await bot.send_message(user.tid, text)
        await bot.send_message(
            user_id, "ok!", reply_markup=keyboard.IDLE_KEYBOARD
        )


@dp.message_handler(commands=["mailing"])  # v2
async def mailing_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    if user_id in ADMINS:
        message_args = msg.get_args()
        try:
            args = mailing_parser.parse_args(shlex.split(message_args))
        except Exception as error:
            await msg.reply(
                "error!\n" + str(error), reply_markup=keyboard.IDLE_KEYBOARD
            )
            return
        for_all = args.all
        groups = args.groups
        message = args.message
        if for_all:
            all_users = manager.get_all_users()
            for user in all_users:
                await bot.send_message(user.tid, message)
            await msg.reply(
                f"ok!\nотправлено пользователям: {len(all_users)}",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        elif groups is not None and len(groups) > 0:
            users = manager.get_users_in_groups(groups)
            for user in users:
                await bot.send_message(user.tid, message)
            await msg.reply(
                f"ok!\nотправлено пользователям: {len(users)}",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )
        else:
            await msg.reply(
                "Не указаны фильтры для отправки. Чтобы отправить сообщение всем, испольуйте ключ -a или --all",
                reply_markup=keyboard.IDLE_KEYBOARD,
            )


@dp.message_handler(state=States.REGISTER)
async def message_handler(msg: types.Message) -> None:
    user_id = msg.from_user.id
    group = msg.text
    ok = manager.group_exists(group)
    if ok:
        manager.set_user_group(user_id, group)
        await States.IDLE.set()
        await bot.send_message(
            user_id,
            f"Ок!\nТеперь ваша группа: {group}",
            reply_markup=keyboard.IDLE_KEYBOARD,
        )
    else:
        await bot.send_message(
            user_id,
            "Не получается найти группу с таким именем :(",
            reply_markup=keyboard.GROUP_KEYBOARD,
        )


@dp.callback_query_handler(lambda c: c.data == "back", state='*')
async def inline_back(callback: types.CallbackQuery) -> None:
    await bot.answer_callback_query(callback.id)
    await bot.edit_message_text(
        "Какое расписание вам нужно?",
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard.SCHEDULE_KEYBOARD,
    )


@dp.callback_query_handler(lambda c: c.data == "grouplist", state='*')
async def inline_group_list(callback: types.CallbackQuery) -> None:
    user_id = callback.from_user.id
    await bot.answer_callback_query(callback.id)
    groups = manager.get_groups()
    await bot.send_message(
        user_id,
        "Список групп:\n"
        + "\n".join([str(g) for g in sorted(groups, key=str)]),
    )


@dp.callback_query_handler(state='*')
async def process_schedule(
    callback: types.CallbackQuery, state: FSMContext
) -> None:
    await bot.answer_callback_query(callback.id)
    day, line = int(callback.data[0]), int(callback.data[1])
    user_id = callback.from_user.id
    user_state = await state.get_state()
    message_id = callback.message.message_id
    if day == 9:  # Time schedule
        await bot.edit_message_text(
            schedule.time_schedule(),
            chat_id=user_id,
            message_id=message_id,
            reply_markup=keyboard.BACK_KEYBOARD,
        )
        # await bot.send_message(user_id, schedule.time_schedule(), reply_markup=keyboard.IDLE_KEYBOARD)
    elif day == 8:  # Is week underline
        await bot.edit_message_text(
            f"Сейчас неделя {'над' if schedule.is_overline() else 'под'} чертой",
            chat_id=user_id,
            message_id=message_id,
            reply_markup=keyboard.BACK_KEYBOARD,
        )
    else:
        user_info: ActiveUser
        data = manager.get_user(user_id)
        if data is None:
            await add_user_critical(user_id)
        else:
            user_info, user_group = data
            if user_state == States.IDLE.state:
                sch = schedule.day_schedule(user_group.group, day, bool(line))
                message_top = f"{Times.weekdays[day]}. {'Над' if bool(line) else 'Под'} чертой.\n\n"
                if len(sch) == 0:
                    await bot.edit_message_text(
                        message_top + "В этот день у вас нет пар",
                        chat_id=user_id,
                        message_id=message_id,
                        reply_markup=keyboard.BACK_KEYBOARD,
                    )
                else:
                    await bot.edit_message_text(
                        message_top + "\n\n".join(sch),
                        chat_id=user_id,
                        message_id=message_id,
                        reply_markup=keyboard.BACK_KEYBOARD,
                    )
                    # await bot.send_message(user_id, "\n\n".join(sch), reply_markup=keyboard.IDLE_KEYBOARD)
            else:
                await bot.edit_message_text(
                    "Вы ещё не указали свою группу!",
                    chat_id=user_id,
                    message_id=message_id,
                    reply_markup=keyboard.BACK_KEYBOARD,
                )


async def morning_scheduler() -> None:
    aioschedule.every().day.at("8:00").do(morning_greeting)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


async def setup(_: Any) -> None:
    asyncio.create_task(morning_scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=setup)
