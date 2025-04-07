from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from db import save_contact, save_wakatime_key
import os
import logging


# Определяем состояния для FSM (конечного автомата)
class RegistrationStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_api_key = State()


router = Router()


# Обработчик для получения file_id отправленной фотографии
@router.message(F.photo)
async def get_photo_id(message: types.Message):
    """
    Выводит file_id полученной фотографии.
    Используйте этот ID в константе WAKATIME_API_KEY_PHOTO_ID
    """
    photo_id = message.photo[-1].file_id
    await message.answer(f"File ID фотографии: {photo_id}")
    logging.info(f"Получен новый file_id фотографии: {photo_id}")


async def start_registration(message: types.Message, state: FSMContext):
    """
    Общая функция для начала процесса регистрации
    """
    username = message.from_user.username
    if username:
        await save_contact(username, message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        f"Привет, @{username}!\nЧтобы завершить регистрацию, отправь свой контакт.",
        reply_markup=keyboard,
    )

    # Устанавливаем состояние - ожидаем контакт
    await state.set_state(RegistrationStates.waiting_for_contact)


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """
    При запуске регистрации сохраняет username (из профиля) и отправляет клавиатуру
    для запроса контакта.
    """
    await start_registration(message, state)


@router.message(Command("register"))
async def register_handler(message: types.Message, state: FSMContext):
    """
    Запускает процесс регистрации заново
    """
    await start_registration(message, state)


@router.message(RegistrationStates.waiting_for_contact, F.content_type.in_({"contact"}))
async def contact_handler(message: types.Message, state: FSMContext):
    """
    Обрабатывает полученный контакт, сохраняет username и запрашивает API ключ.
    """
    username = message.from_user.username
    if username:
        await save_contact(username, message.from_user.id)

        # Удаляем клавиатуру с запросом контакта
        await message.answer(
            f"Спасибо, @{username}!", reply_markup=types.ReplyKeyboardRemove()
        )

        # Инструкция для получения API ключа
        api_key_instructions = (
            f"Теперь отправь мне свой WakaTime API ключ.\n\n"
            f"Для этого:\n"
            f"1. Зайдите на страницу: https://wakatime.com/settings/account\n"
            f"2. В самом верху в разделе API Keys есть Secret API Key, нажмите на него и увидите ключ(скриншот выше)\n"
            f"3. Скопируйте ключ и отправьте его мне"
        )

        # Путь к файлу с изображением
        photo_path = os.path.join("images", "wakatime_api_key.png")

        try:
            # Проверяем существование файла и отправляем фото
            if os.path.isfile(photo_path):
                photo = FSInputFile(photo_path)
                await message.answer_photo(photo=photo, caption=api_key_instructions)
            else:
                # Если файл не найден, отправляем только текст
                logging.warning(f"Файл изображения {photo_path} не найден")
                await message.answer(api_key_instructions)
        except Exception as e:
            # В случае ошибки отправляем только текстовые инструкции
            logging.error(f"Ошибка при отправке фото: {e}")
            await message.answer(api_key_instructions)

        # Устанавливаем состояние - ожидаем API ключ
        await state.set_state(RegistrationStates.waiting_for_api_key)
    else:
        await message.answer(
            "Извините, у вас нет username в профиле. Регистрация невозможна."
        )
        await state.clear()


@router.message(RegistrationStates.waiting_for_api_key)
async def api_key_handler(message: types.Message, state: FSMContext):
    """
    Обрабатывает полученный API ключ и завершает регистрацию.
    """
    api_key = message.text.strip()

    if not api_key:
        await message.answer("Пожалуйста, отправь мне свой WakaTime API ключ.")
        return

    await save_wakatime_key(message.from_user.id, api_key)

    await message.answer(
        "WakaTime API ключ сохранён! Регистрация успешно завершена.\n\n"
        "Теперь используй команды:\n"
        "/top - показать топ по времени кодинга за сегодня\n"
        "/week - показать топ по времени кодинга за неделю"
    )

    # Очищаем состояние
    await state.clear()
