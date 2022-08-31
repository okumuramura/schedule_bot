import pytest

from schedule_bot.updater.parse import parse_lesson_exp, Lesson


@pytest.mark.parametrize(
    ('lesson_str', 'expected'),
    [
        (
            '(51) (лекц) Программирование,  Вдовин А.Ю., 122в',
            Lesson('Программирование', 'Вдовин А.Ю.', '122в', 'лек', '51')
        ),
        (
            '(66) (л/р) Основы программирования на С++, Кайсина И.А. 5-302',
            Lesson('Основы программирования на С++', 'Кайсина И.А.', '5-302', 'лаб', '66')
        ),
        (
            '(21) (лекц) Мастер-класс "Реклама и связи с общественностью", Чукавин С.И.1-301',
            Lesson('Мастер-класс "Реклама и связи с общественностью"', 'Чукавин С.И.', '1-301', 'лек', '21')
        ),
        (
            '(78) (лекц) Управление проектами, Титова О.В., (ee.istu.ru)',
            Lesson('Управление проектами', 'Титова О.В.', 'ee.istu.ru', 'лек', '78')
        )
    ]
)
def test_parse(lesson_str: str, expected: Lesson):
    assert parse_lesson_exp(lesson_str) == expected
