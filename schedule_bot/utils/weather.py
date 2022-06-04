import asyncio
import logging
from typing import Optional

import aiohttp

from schedule_bot import info

API_KEY = info.WEATHER_KEY

ICONS = {
    1: ":sun:",
    2: ":sun:",
    3: ":sun_behind_small_cloud:",
    4: ":sun_behind_small_cloud:",
    5: ":sun_behind_cloud:",
    6: ":sun_behind_cloud:",
    7: ":cloud:",
    8: ":cloud:",
    11: ":fog:",
    12: ":cloud_with_rain:",
    13: ":cloud_with_rain:",
    14: ":sun_behind_rain_cloud:",
    15: ":cloud_with_lightning_and_rain:",
    16: ":cloud_with_lightning_and_rain:",
    17: ":cloud_with_lightning_and_rain:",
    18: ":cloud_with_rain:",
    19: ":cloud_with_snow:",
    20: ":cloud_with_snow:",
    21: ":cloud_with_snow:",
    22: ":cloud_with_snow:",
    23: ":cloud_with_snow:",
    24: ":ice:",
    25: ":cloud_with_snow:",
    26: ":cloud_with_rain:",
    29: ":cloud_with_snow:",
    30: ":hot_face:",
    31: ":cold_face:",
    32: ":dashing_away:",
}


async def get_weather(location: int = 296181) -> Optional[str]:
    async with aiohttp.ClientSession() as session:
        weather_api_url = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location}?apikey={key}&language=ru-ru&details=true&metric=true"
        async with session.get(
            weather_api_url.format(location=location, key=API_KEY)
        ) as resp:
            if resp.status == 200:
                weather = await resp.json()
                try:
                    day = weather["DailyForecasts"][0]["Day"]
                    temp = weather["DailyForecasts"][0]["Temperature"]
                    icon_code = day["Icon"]
                    icon = ICONS.get(icon_code, "")
                    phrase = day["ShortPhrase"]
                    temp_max = temp["Maximum"]["Value"]
                    temp_min = temp["Minimum"]["Value"]
                    wind = day["Wind"]
                    wind_speed = wind["Speed"]["Value"]
                    _ = wind["Speed"]["Unit"]
                    wind_direction = wind["Direction"]["Localized"]
                    wind_speed_formated = float(wind_speed) * 5 / 18
                except KeyError as err:
                    logging.error(err)
                    return None

                result = (
                    "Погода:\n"
                    f"{int(temp_max):+}°..{int(temp_min):+}°\n"
                    f"{icon} {phrase}\n"
                    f"Ветер {wind_direction} {wind_speed_formated:.1f} м/с\n"
                )
                return result
            else:
                logging.warning("weather page status code: %d", resp.status)
                return None


if __name__ == "__main__":
    result = asyncio.run(get_weather())
    print(result)
