from aiogram import types
from aiogram.utils.emoji import emojize

from schedule_bot.manager import manager


class Keyboard:
    def __init__(self) -> None:
        self.IDLE_KEYBOARD = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.SCHEDULE_KEYBOARD = types.InlineKeyboardMarkup(row_width=2)
        self.BACK_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)
        self.GROUP_KEYBOARD = types.InlineKeyboardMarkup(row_width=1)

        self.IDLE_KEYBOARD.row(
            types.KeyboardButton(text='Сегодня'),
            types.KeyboardButton(text='Завтра'),
        )
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text='Расписание'))
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text='Сейчас'))
        self.IDLE_KEYBOARD.add(types.KeyboardButton(text='Выйти'))

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Понедельник :arrow_up:'), callback_data='01'
            ),
            types.InlineKeyboardButton(
                emojize('Понедельник :arrow_down:'), callback_data='00'
            ),
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Вторник :arrow_up:'), callback_data='11'
            ),
            types.InlineKeyboardButton(
                emojize('Вторник :arrow_down:'), callback_data='10'
            ),
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Среда :arrow_up:'), callback_data='21'
            ),
            types.InlineKeyboardButton(
                emojize('Среда :arrow_down:'), callback_data='20'
            ),
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Четверг :arrow_up:'), callback_data='31'
            ),
            types.InlineKeyboardButton(
                emojize('Четверг :arrow_down:'), callback_data='30'
            ),
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Пятница :arrow_up:'), callback_data='41'
            ),
            types.InlineKeyboardButton(
                emojize('Пятница :arrow_down:'), callback_data='40'
            ),
        )

        self.SCHEDULE_KEYBOARD.row(
            types.InlineKeyboardButton(
                emojize('Суббота :arrow_up:'), callback_data='51'
            ),
            types.InlineKeyboardButton(
                emojize('Суббота :arrow_down:'), callback_data='50'
            ),
        )

        self.SCHEDULE_KEYBOARD.add(
            types.InlineKeyboardButton('Время', callback_data='99')
        )

        self.SCHEDULE_KEYBOARD.add(
            types.InlineKeyboardButton('Неделя', callback_data='88')
        )

        self.BACK_KEYBOARD.add(
            types.InlineKeyboardButton('Назад', callback_data='back')
        )

        self.GROUP_KEYBOARD.add(
            types.InlineKeyboardButton(
                'Список групп', callback_data='grouplist'
            )
        )

    @staticmethod
    def build_settings_keyboard(user_id: int) -> types.InlineKeyboardMarkup:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        fields = (
            'Утренние сообщения',
        )
        settings = manager.get_user_settings_by_telegram_id(user_id)
        if not settings:
            return None

        for message, value in zip(fields, settings.values()):
            keyboard.add(
                types.InlineKeyboardButton(
                    f'{message}: {"ON" if value else "OFF"}',
                    callback_data=('settings_vip_%d' % (not value))
                )
            )
        return keyboard
