"""
Вспомогательные функции, используемые в разных обработчиках бота.
"""

def format_time(minutes):
    """
    Форматирует время в минутах в дни, часы и минуты.
    
    Args:
        minutes (float): время в минутах
        
    Returns:
        str: отформатированная строка времени
    
    Примеры:
        30 -> "30 мин"
        90 -> "1 ч 30 мин"
        1500 -> "1 д 1 ч 0 мин"
    """
    if minutes < 60:
        return f"{int(minutes)} мин"
    
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if hours < 24:
        return f"{hours} ч {mins} мин"
    else:
        days = hours // 24
        remaining_hours = hours % 24
        return f"{days} д {remaining_hours} ч {mins} мин"

def format_username(username):
    """
    Форматирует имя пользователя в HTML-ссылку,
    чтобы избежать упоминаний и уведомлений.
    
    Args:
        username (str): имя пользователя Telegram
        
    Returns:
        str: HTML-ссылка на профиль пользователя
    """
    return f'<a href="https://t.me/{username}">{username}</a>' 