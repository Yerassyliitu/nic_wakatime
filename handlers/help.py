from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F

router = Router()

@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help, показывающий доступные команды."""
    
    # Разные тексты для личного чата и групп
    if message.chat.type == "private":
        help_text = """<b>Доступные команды:</b>

<b>Регистрация:</b>
/start - Начать взаимодействие с ботом
/setkey - Установить ключ WakaTime API

<b>Статистика:</b>
/top - Показать статистику за день
/week - Показать статистику за неделю
/month - Показать статистику за месяц (кэшируется)
/year - Показать статистику за год (кэшируется)

<b>Помощь:</b>
/help - Показать это сообщение"""
    else:
        help_text = """<b>Доступные команды бота WakaTime:</b>

/top - Статистика за день
/week - Статистика за неделю
/month - Статистика за месяц
/year - Статистика за год

Для регистрации и настройки перейдите в <a href="https://t.me/niciwaka_bot">личный чат с ботом</a>"""
    
    await message.answer(help_text, parse_mode="HTML") 