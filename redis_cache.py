import json
import logging
import os
import sys
import redis
import traceback
from datetime import datetime

# Настройка логирования, если еще не настроено
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

# Получаем URL Redis из переменной окружения или используем значение по умолчанию
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
logging.info(f"Используем Redis URL: {REDIS_URL}")

# Создаем соединение с Redis
try:
    redis_client = redis.from_url(REDIS_URL)
except Exception as e:
    logging.error(f"Ошибка создания клиента Redis: {e}\n{traceback.format_exc()}")
    redis_client = None

# Ключи для кэша
MONTH_CACHE_KEY = "wakatime:month_stats"
YEAR_CACHE_KEY = "wakatime:year_stats"

# Время жизни кэша в секундах
MONTH_CACHE_TTL = 3600  # 1 час
YEAR_CACHE_TTL = 86400  # 24 часа

def init_redis():
    """Проверяем соединение с Redis и логируем результат"""
    global redis_client
    
    # Если клиент не инициализирован, пробуем создать заново
    if redis_client is None:
        try:
            redis_client = redis.from_url(REDIS_URL)
        except Exception as e:
            logging.error(f"Ошибка создания клиента Redis: {e}\n{traceback.format_exc()}")
            return False
    
    # Проверяем соединение
    try:
        redis_client.ping()
        logging.info(f"Успешное подключение к Redis: {REDIS_URL}")
        return True
    except redis.RedisError as e:
        logging.error(f"Ошибка подключения к Redis: {e}\n{traceback.format_exc()}")
        return False

def save_month_stats(stats_data):
    """
    Сохраняет статистику за месяц в Redis
    
    Args:
        stats_data: Список кортежей (username, minutes)
    """
    if not init_redis():
        logging.error("Redis не инициализирован. Невозможно сохранить данные.")
        return False
        
    data_to_save = {
        "timestamp": datetime.now().isoformat(),
        "data": [(username, float(minutes)) for username, minutes in stats_data]
    }
    try:
        redis_client.setex(
            MONTH_CACHE_KEY, 
            MONTH_CACHE_TTL, 
            json.dumps(data_to_save, ensure_ascii=False)
        )
        logging.info(f"Месячная статистика обновлена в кэше, {len(stats_data)} записей")
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении месячной статистики: {e}\n{traceback.format_exc()}")
        return False

def get_month_stats():
    """
    Получает статистику за месяц из Redis
    
    Returns:
        Список кортежей (username, minutes) или None, если кэш отсутствует
    """
    if not init_redis():
        logging.error("Redis не инициализирован. Невозможно получить данные.")
        return None
        
    try:
        data = redis_client.get(MONTH_CACHE_KEY)
        if not data:
            logging.warning("Кэш месячной статистики не найден")
            return None
        
        parsed_data = json.loads(data)
        timestamp = datetime.fromisoformat(parsed_data["timestamp"])
        stats = parsed_data["data"]
        
        # Убедимся, что вернулся корректный формат данных
        if not stats or not isinstance(stats, list):
            logging.error(f"Неверный формат данных в кэше месячной статистики: {stats}")
            return None
            
        # Преобразуем JSON данные обратно в кортежи с числовыми значениями
        stats = [(username, float(minutes)) for username, minutes in stats]
        
        age_seconds = (datetime.now() - timestamp).total_seconds()
        logging.info(f"Данные из кэша за месяц получены, возраст: {age_seconds:.1f} сек, записей: {len(stats)}")
        
        return stats
    except Exception as e:
        logging.error(f"Ошибка при получении месячной статистики из кэша: {e}\n{traceback.format_exc()}")
        return None

def save_year_stats(stats_data):
    """
    Сохраняет статистику за год в Redis
    
    Args:
        stats_data: Список кортежей (username, minutes)
    """
    if not init_redis():
        logging.error("Redis не инициализирован. Невозможно сохранить данные.")
        return False
        
    data_to_save = {
        "timestamp": datetime.now().isoformat(),
        "data": [(username, float(minutes)) for username, minutes in stats_data]
    }
    try:
        redis_client.setex(
            YEAR_CACHE_KEY, 
            YEAR_CACHE_TTL, 
            json.dumps(data_to_save, ensure_ascii=False)
        )
        logging.info(f"Годовая статистика обновлена в кэше, {len(stats_data)} записей")
        return True
    except Exception as e:
        logging.error(f"Ошибка при сохранении годовой статистики: {e}\n{traceback.format_exc()}")
        return False

def get_year_stats():
    """
    Получает статистику за год из Redis
    
    Returns:
        Список кортежей (username, minutes) или None, если кэш отсутствует
    """
    if not init_redis():
        logging.error("Redis не инициализирован. Невозможно получить данные.")
        return None
        
    try:
        data = redis_client.get(YEAR_CACHE_KEY)
        if not data:
            logging.warning("Кэш годовой статистики не найден")
            return None
        
        parsed_data = json.loads(data)
        timestamp = datetime.fromisoformat(parsed_data["timestamp"])
        stats = parsed_data["data"]
        
        # Убедимся, что вернулся корректный формат данных
        if not stats or not isinstance(stats, list):
            logging.error(f"Неверный формат данных в кэше годовой статистики: {stats}")
            return None
        
        # Преобразуем JSON данные обратно в кортежи с числовыми значениями
        stats = [(username, float(minutes)) for username, minutes in stats]
        
        age_seconds = (datetime.now() - timestamp).total_seconds()
        logging.info(f"Данные из кэша за год получены, возраст: {age_seconds:.1f} сек, записей: {len(stats)}")
        
        return stats
    except Exception as e:
        logging.error(f"Ошибка при получении годовой статистики из кэша: {e}\n{traceback.format_exc()}")
        return None 