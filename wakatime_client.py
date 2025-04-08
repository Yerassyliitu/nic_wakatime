import aiohttp
import logging
from datetime import datetime, timedelta


async def get_coding_time_today(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) кодирования
    за сегодняшний день. Учитывает все категории.

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

    # Если данных нет или структура ответа не соответствует ожидаемой
    if not data.get("data") or not isinstance(data["data"], list) or not data["data"]:
        logging.warning(f"Пустой или некорректный ответ от WakaTime API")
        return 0.0

    # Берём суммарное время (grand_total) вместо фильтрации по категориям
    try:
        day_data = data["data"][0]  # Данные за текущий день
        total_seconds = day_data.get("grand_total", {}).get("total_seconds", 0)
        
        # Выводим детальную информацию для отладки
        logging.info(f"WakaTime API ответ: {total_seconds} секунд за сегодня")
        
        return total_seconds / 60.0
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"Ошибка при обработке ответа WakaTime API: {e}")
        return 0.0


async def get_coding_time_week(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) кодирования
    за последние 7 дней (включая сегодняшний день). Учитывает все категории.

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

    # Если данных нет или структура ответа не соответствует ожидаемой
    if not data.get("data") or not isinstance(data["data"], list):
        logging.warning(f"Пустой или некорректный ответ от WakaTime API")
        return 0.0

    # Суммируем grand_total.total_seconds за все дни недели
    total_seconds = 0
    try:
        # Итерируемся по дням недели в ответе
        for day_data in data["data"]:
            total_seconds += day_data.get("grand_total", {}).get("total_seconds", 0)
        
        # Выводим детальную информацию для отладки
        logging.info(f"WakaTime API ответ: {total_seconds} секунд за неделю")
        
        return total_seconds / 60.0
    except (KeyError, TypeError) as e:
        logging.error(f"Ошибка при обработке ответа WakaTime API: {e}")
        return 0.0


async def get_coding_time_month(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) кодирования
    за последние 30 дней (включая сегодняшний день). Учитывает все категории.

    :param waka_key: API ключ пользователя.
    :return: Общее количество минут кодинга за месяц.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=29)  # 30 дней: сегодня + 29 предыдущих
    url = "https://wakatime.com/api/v1/users/current/summaries"
    params = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "api_key": waka_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка запроса к WakaTime API за месяц: статус {resp.status}")
                return 0.0
            data = await resp.json()

    # Если данных нет или структура ответа не соответствует ожидаемой
    if not data.get("data") or not isinstance(data["data"], list):
        logging.warning(f"Пустой или некорректный ответ от WakaTime API")
        return 0.0

    # Суммируем grand_total.total_seconds за все дни месяца
    total_seconds = 0
    try:
        # Итерируемся по дням месяца в ответе
        for day_data in data["data"]:
            total_seconds += day_data.get("grand_total", {}).get("total_seconds", 0)
        
        # Выводим детальную информацию для отладки
        logging.info(f"WakaTime API ответ: {total_seconds} секунд за месяц")
        
        return total_seconds / 60.0
    except (KeyError, TypeError) as e:
        logging.error(f"Ошибка при обработке ответа WakaTime API: {e}")
        return 0.0


async def get_coding_time_year(waka_key: str) -> float:
    """
    Запрашивает у WakaTime суммарное время (в минутах) кодирования
    за последние 365 дней (включая сегодняшний день). Учитывает все категории.

    :param waka_key: API ключ пользователя.
    :return: Общее количество минут кодинга за год.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=364)  # 365 дней: сегодня + 364 предыдущих
    url = "https://wakatime.com/api/v1/users/current/summaries"
    params = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "api_key": waka_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                logging.error(f"Ошибка запроса к WakaTime API за год: статус {resp.status}")
                return 0.0
            data = await resp.json()

    # Если данных нет или структура ответа не соответствует ожидаемой
    if not data.get("data") or not isinstance(data["data"], list):
        logging.warning(f"Пустой или некорректный ответ от WakaTime API")
        return 0.0

    # Суммируем grand_total.total_seconds за все дни года
    total_seconds = 0
    try:
        # Итерируемся по дням года в ответе
        for day_data in data["data"]:
            total_seconds += day_data.get("grand_total", {}).get("total_seconds", 0)
        
        # Выводим детальную информацию для отладки
        logging.info(f"WakaTime API ответ: {total_seconds} секунд за год")
        
        return total_seconds / 60.0
    except (KeyError, TypeError) as e:
        logging.error(f"Ошибка при обработке ответа WakaTime API: {e}")
        return 0.0