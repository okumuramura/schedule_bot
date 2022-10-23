from typer import Typer

from schedule_bot import METRICS_ENABLE
from schedule_bot.metrics import start_metrics
from schedule_bot.bot import bot

app = Typer(name='schedule bot')


@app.command('start')
def start():
    if METRICS_ENABLE:
        start_metrics()
    bot.start_polling()


if __name__ == '__main__':
    app()
