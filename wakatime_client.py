import aiohttp
import logging
from datetime import datetime, timedelta


async def get_coding_time_today(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) по категории 'Coding'
    за сегодняшний день.

    Аутентификация осуществляется посредством передачи API ключа в параметре запроса.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    url = "https://wakatime.com/api/v1/users/current/summaries"
    params = {"start": today, "end": today, "api_key": waka_key}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка запроса к WakaTime API: статус {resp.status}")
                return 0.0
            data = await resp.json()

    total_seconds = 0
    for day in data.get("data", []):
        for category in day.get("categories", []):
            if category.get("name") == "Coding":
                total_seconds += category.get("total_seconds", 0)
    return total_seconds / 60.0


async def get_coding_time_week(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) по категории 'Coding'
    за последние 7 дней (включая сегодняшний день).

    :param waka_key: API ключ пользователя.
    :return: Общее количество минут кодинга за неделю.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)  # 7 дней: сегодня + 6 предыдущих
    url = "https://wakatime.com/api/v1/users/current/summaries"
    params = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "api_key": waka_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка запроса к WakaTime API за неделю: статус {resp.status}")
                return 0.0
            data = await resp.json()

    total_seconds = 0
    for day in data.get("data", []):
        for category in day.get("categories", []):
            if category.get("name") == "Coding":
                total_seconds += category.get("total_seconds", 0)
    return total_seconds / 60.0
