#!/usr/bin/env python3
"""
Скрипт для периодического обновления кэша годовой статистики.
Запускается через supervisor каждый день в 00:00.
"""
import asyncio
import logging
import os
import sys
import traceback

from db import init_db_pool, get_all_users
from wakatime_client import get_coding_time_year
from redis_cache import save_year_stats, init_redis
from config import DATABASE_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def update_year_cache():
    """Собирает статистику за год и обновляет кэш"""
    logging.info("Начинаем обновление годовой статистики...")
    
    # Инициализируем подключение к базе данных
    try:
        await init_db_pool(DATABASE_URL)
        logging.info("Подключение к базе данных установлено")
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}\n{traceback.format_exc()}")
        return
    
    # Проверяем подключение к Redis
    if not init_redis():
        logging.error("Не удалось подключиться к Redis. Отмена обновления кэша.")
        return
    
    # Получаем список пользователей
    try:
        users = await get_all_users()
        if not users:
            logging.warning("Не найдено пользователей для обновления статистики")
            return
    except Exception as e:
        logging.error(f"Ошибка получения списка пользователей: {e}\n{traceback.format_exc()}")
        return
    
    # Собираем статистику
    logging.info(f"Начинаем сбор годовой статистики для {len(users)} пользователей")
    leaderboard = []
    
    for tg_id, username, waka_key in users:
        if not waka_key:
            continue
        try:
            logging.info(f"Получаем годовую статистику для @{username}")
            coding_minutes = await get_coding_time_year(waka_key)
            logging.info(f"Статистика @{username}: {coding_minutes} минут за год")
            leaderboard.append((username, coding_minutes))
        except Exception as e:
            logging.error(f"Ошибка получения годовой статистики для @{username}: {e}\n{traceback.format_exc()}")
    
    # Сохраняем в кэш
    if leaderboard:
        logging.info(f"Собрана годовая статистика для {len(leaderboard)} пользователей. Сохраняем в кэш...")
        for username, minutes in leaderboard:
            logging.info(f"  @{username}: {minutes} минут")
            
        if save_year_stats(leaderboard):
            logging.info(f"Годовая статистика успешно обновлена для {len(leaderboard)} пользователей")
        else:
            logging.error("Не удалось сохранить годовую статистику в кэш")
    else:
        logging.warning("Нет данных для сохранения в кэш")

if __name__ == "__main__":
    try:
        # Установим текущую директорию на директорию скрипта для правильной загрузки модулей
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Запустим обновление кэша
        asyncio.run(update_year_cache())
        logging.info("Скрипт обновления годового кэша завершен успешно")
    except Exception as e:
        logging.error(f"Ошибка при выполнении скрипта обновления годового кэша: {e}\n{traceback.format_exc()}")
        sys.exit(1) 