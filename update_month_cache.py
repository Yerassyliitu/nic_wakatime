#!/usr/bin/env python3
"""
Скрипт для периодического обновления кэша месячной статистики.
Запускается через cron каждый час.
"""
import asyncio
import logging
import os
import sys

from db import init_db_pool, get_all_users
from wakatime_client import get_coding_time_month
from redis_cache import save_month_stats, init_redis
from config import DATABASE_URL

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def update_month_cache():
    """Собирает статистику за месяц и обновляет кэш"""
    logging.info("Начинаем обновление месячной статистики...")
    
    # Инициализируем подключение к базе данных
    try:
        await init_db_pool(DATABASE_URL)
        logging.info("Подключение к базе данных установлено")
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return
    
    # Проверяем подключение к Redis
    if not init_redis():
        logging.error("Не удалось подключиться к Redis. Отмена обновления кэша.")
        return
    
    # Получаем список пользователей
    users = await get_all_users()
    if not users:
        logging.warning("Не найдено пользователей для обновления статистики")
        return
    
    # Собираем статистику
    logging.info(f"Начинаем сбор статистики для {len(users)} пользователей")
    leaderboard = []
    
    for tg_id, username, waka_key in users:
        if not waka_key:
            continue
        try:
            logging.info(f"Получаем статистику для @{username}")
            coding_minutes = await get_coding_time_month(waka_key)
            leaderboard.append((username, coding_minutes))
        except Exception as e:
            logging.error(f"Ошибка получения статистики для @{username}: {e}")
    
    # Сохраняем в кэш
    if leaderboard:
        if save_month_stats(leaderboard):
            logging.info(f"Месячная статистика успешно обновлена для {len(leaderboard)} пользователей")
        else:
            logging.error("Не удалось сохранить месячную статистику в кэш")
    else:
        logging.warning("Нет данных для сохранения в кэш")

if __name__ == "__main__":
    asyncio.run(update_month_cache()) 