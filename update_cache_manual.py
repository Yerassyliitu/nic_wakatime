#!/usr/bin/env python3
"""
Скрипт для ручного обновления кэша месячной и годовой статистики.
Запускается вручную, полезен для тестирования и отладки.
"""
import asyncio
import logging
import sys

from update_month_cache import update_month_cache
from update_year_cache import update_year_cache

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

async def update_all_caches():
    """Обновляет все кэши статистики один за другим"""
    
    logging.info("====== ОБНОВЛЕНИЕ МЕСЯЧНОЙ СТАТИСТИКИ ======")
    try:
        await update_month_cache()
        logging.info("Обновление месячной статистики завершено успешно")
    except Exception as e:
        logging.error(f"Ошибка при обновлении месячной статистики: {e}")
    
    logging.info("\n====== ОБНОВЛЕНИЕ ГОДОВОЙ СТАТИСТИКИ ======")
    try:
        await update_year_cache()
        logging.info("Обновление годовой статистики завершено успешно")
    except Exception as e:
        logging.error(f"Ошибка при обновлении годовой статистики: {e}")
    
    logging.info("\n====== ОБНОВЛЕНИЕ КЭША ЗАВЕРШЕНО ======")

if __name__ == "__main__":
    logging.info("Запуск ручного обновления кэша...")
    try:
        asyncio.run(update_all_caches())
        logging.info("Скрипт ручного обновления кэша завершен успешно")
    except Exception as e:
        logging.error(f"Ошибка при выполнении скрипта ручного обновления кэша: {e}")
        sys.exit(1) 