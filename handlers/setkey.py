from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from db import save_wakatime_key

router = Router()

@router.message(Command("setkey"))
async def setkey_handler(message: types.Message, command: CommandObject):
    """
    Сохраняет WakaTime API ключ, переданный пользователем.
    """
    if not command.args:
        await message.answer("Пожалуйста, укажи свой WakaTime API ключ: /setkey &lt;твой API ключ&gt;")
        return
    await save_wakatime_key(message.from_user.id, command.args.strip())
    await message.answer("WakaTime API ключ сохранён! Теперь используй /top или /week для получения статистики.")
