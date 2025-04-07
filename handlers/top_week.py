from aiogram import Router, types
from aiogram.filters import Command
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
    """
    users = await get_all_users()
    if not users:
        await message.answer("Пока никто не добавил свой WakaTime API ключ. Используй /setkey.")
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
