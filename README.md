# Schedule bot
Telegram bot and gui interface for make schedules.

## Features
- GUI interface for creating and editing schedules.
- Async Telegram bot.
- ORM Database and data schemes.
- Downloader and parser for ISTU University.
- Weather module (accuweather.com)
- Current lesson command (now and next)

## Bot creating
[Official Telegram tutorial](https://core.telegram.org/bots#3-how-do-i-create-a-bot).  
Also you can add commands prompts via sending `/setcommands` command to [@BotFather](https://t.me/BotFather) with message like this:  
```
today - today schedule
tomorrow - tommorow schedule
now - current lesson
schedule - schedule menu
week - current week
times - time schedule
invite - create invite link
logout - logout user
```

## Docker compose
```
docker-compose up -d
```

## Configurate
You can configurate bot app via config file or env variables.  
Example of `config.toml` file:
```toml
[bot]
key = "<your bot api key>"
admins = []  # some telegram ids

[db]
driver = "postgresql"
host = "postgres:password@localhost/schedule"

[redis]
host = "localhost"
port = 6379

[tools]
    [tools.weather]
    key = "<your accuweather.com api key>"
    location = 294021  # location id on accuweather.com
```

## GUI
> `Warning: not working now`
```
python -m schedule_bot gui
```
