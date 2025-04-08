from aiogram import Router, types, F
from aiogram.filters import Command
from db import get_all_users
from wakatime_client import get_coding_time_month
from redis_cache import get_month_stats, save_month_stats
from utils import format_time, format_username

router = Router()

@router.message(Command("month"))
async def top_month_handler(message: types.Message):
    """
    Формирует лидерборд участников по времени кодинга за последние 30 дней.
    Отображает username как ссылку и время в формате часы и минуты.
    Работает как в личных сообщениях, так и в группах.
    Использует кэш Redis для ускорения ответа.
    """
    # Проверяем, не групповой ли это чат
    is_private = message.chat.type == "private"
    
    # Пытаемся получить данные из кэша
    cached_stats = get_month_stats()
    
    # Если данные есть в кэше, используем их
    if cached_stats is not None:
        leaderboard = cached_stats
    else:
        # Если данных в кэше нет, собираем их обычным способом
        users = await get_all_users()
        if not users:
            # Изменяем сообщение для групп
            if is_private:
                await message.answer("Пока никто не добавил свой WakaTime API ключ. Используй /register.")
            else:
                bot_username = (await message.bot.get_me()).username
                await message.answer(
                    "Пока никто не добавил свой WakaTime API ключ. "
                    f"Для регистрации напишите мне в личные сообщения: https://t.me/{bot_username}"
                )
            return
            
        # Сообщаем пользователю, что идет сбор данных
        status_message = await message.answer("Собираем данные за месяц... Это может занять некоторое время.")
        
        leaderboard = []
        for tg_id, username, waka_key in users:
            if not waka_key:
                continue
            coding_minutes = await get_coding_time_month(waka_key)
            leaderboard.append((username, coding_minutes))
        
        # Сохраняем данные в кэш
        save_month_stats(leaderboard)
        
        # Удаляем статусное сообщение
        try:
            await status_message.delete()
        except:
            pass
    
    # Сортируем и форматируем результаты
    leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
    lines = ["<b>Топ участников (Coding за месяц):</b>"]
    
    for rank, (username, minutes) in enumerate(leaderboard, start=1):
        lines.append(f"{rank}. {format_username(username)} — {format_time(minutes)}")
    
    await message.answer("\n".join(lines), parse_mode="HTML") 