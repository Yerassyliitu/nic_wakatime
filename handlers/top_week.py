from aiogram import Router, types
from aiogram.filters import Command, ChatTypeFilter
from aiogram.types import ChatType
from db import get_all_users
from wakatime_client import get_coding_time_week

router = Router()

def format_time(minutes):
    """
    Форматирует время в минутах в часы и минуты.
    Например: 90 минут -> 1 ч 30 мин
    """
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    
    if hours > 0:
        return f"{hours} ч {mins} мин"
    else:
        return f"{mins} мин"

@router.message(Command("top_week"))
async def top_week_handler(message: types.Message):
    """
    Формирует лидерборд участников по времени кодинга за последние 7 дней.
    Отображает @username и время в формате часы и минуты.
    Работает как в личных сообщениях, так и в группах.
    """
    # Проверяем, не групповой ли это чат и есть ли у пользователя права на просмотр
    if not message.chat.type == ChatType.PRIVATE:
        # В будущем можно добавить проверку админских прав пользователя в группе
        pass
    
    users = await get_all_users()
    if not users:
        # Изменяем сообщение для групп
        if message.chat.type == ChatType.PRIVATE:
            await message.answer("Пока никто не добавил свой WakaTime API ключ. Используй /register.")
        else:
            bot_username = (await message.bot.get_me()).username
            await message.answer(
                "Пока никто не добавил свой WakaTime API ключ. "
                f"Для регистрации напишите мне в личные сообщения: https://t.me/{bot_username}"
            )
        return
        
    leaderboard = []
    for tg_id, username, waka_key in users:
        if not waka_key:
            continue
        coding_minutes = await get_coding_time_week(waka_key)
        leaderboard.append((username, coding_minutes))
    
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    lines = ["<b>Топ участников (Coding за неделю):</b>"]
    
    for rank, (username, minutes) in enumerate(leaderboard, start=1):
        lines.append(f"{rank}. @{username} — {format_time(minutes)}")
    
    await message.answer("\n".join(lines), parse_mode="HTML") 