from aiogram import Router, types, F
from aiogram.filters import Command
from db import get_all_users
from wakatime_client import get_coding_time_today
from utils import format_time, format_username

router = Router()

@router.message(Command("day"))
async def top_day_handler(message: types.Message):
    """
    Формирует лидерборд участников по времени кодинга за сегодня.
    Отображает username как ссылку и время в формате часы и минуты.
    Работает как в личных сообщениях, так и в группах.
    """
    # Проверяем, не групповой ли это чат и есть ли у пользователя права на просмотр
    is_private = message.chat.type == "private"
    
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
        
    leaderboard = []
    for tg_id, username, waka_key in users:
        if not waka_key:
            continue
        coding_minutes = await get_coding_time_today(waka_key)
        leaderboard.append((username, coding_minutes))
    
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    lines = ["<b>Топ участников (Coding за сегодня):</b>"]
    
    for rank, (username, minutes) in enumerate(leaderboard, start=1):
        lines.append(f"{rank}. {format_username(username)} — {format_time(minutes)}")
    
    await message.answer("\n".join(lines), parse_mode="HTML") 