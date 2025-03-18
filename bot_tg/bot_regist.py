from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from sqlalchemy import insert
from value import (
    REGISTER_FIRST_NAME, REGISTER_LAST_NAME, REGISTER_PHONE, REGISTER_METOD_CATCH,
    REGISTER_GEAR_MAIN, REGISTER_BIO, REGISTER_ALIAS, REGISTER_PHOTO,REGISTER_BIRTH,
    PHOTO_DIR, MESSAGES, USER_ID_FIELD, IMAGE_PATH_FIELD, CALLBACK_CANCEL_EDIT, CALLBACK_REGISTER
)
import os
import re
import logging
from db_connect import *
from bot_ui import get_main_keyboard
from datetime import datetime
from bot_minio import *
import io

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



async def register_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Начало процесса регистрации."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    message = query.message

    # Отправляем сообщение о начале регистрации
    loading_message = await message.reply_text(MESSAGES["loading_message"], quote=False)

    try:
        await loading_message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о загрузке: {e}")

    await message.reply_text("Введите ваше имя:", reply_markup=ReplyKeyboardRemove())
    return REGISTER_FIRST_NAME


async def register_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 1: Сохранение имени."""
    context.user_data['first_name'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел имя: {context.user_data['first_name']}")
    await update.message.reply_text("Введите вашу фамилию:")
    return REGISTER_LAST_NAME


async def register_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 2: Сохранение фамилии."""
    context.user_data['last_name'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел фамилию: {context.user_data['last_name']}")
    await update.message.reply_text("Введите ваш номер телефона (в формате 7XXXXXXXXXX или 375XXXXXXXXX) или введите '-' если не хотите указывать:")
    return REGISTER_PHONE


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 3: Сохранение номера телефона с валидацией."""
    phone_number = update.message.text.strip()
    print(phone_number)
    if phone_number == "-":
        context.user_data['phone_number'] = None
        await update.message.reply_text("Введите основной метод ловли:")
        return REGISTER_METOD_CATCH
    # Проверяем формат номера телефона
    if not re.match(r'^(7\d{10}|375\d{9})$', phone_number):
        await update.message.reply_text("Некорректный формат телефона. Введите номер в формате 7XXXXXXXXXX или 375XXXXXXXXX:")
        return REGISTER_PHONE
    context.user_data['phone_number'] = phone_number
    logger.info(f"Пользователь {update.effective_user.id} ввел телефон: {context.user_data['phone_number']}")
    await update.message.reply_text("Введите основной метод ловли:")
    return REGISTER_METOD_CATCH


async def register_metod_catch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 4: Сохранение метода ловли."""
    context.user_data['metod_catch'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел метод ловли: {context.user_data['metod_catch']}")
    await update.message.reply_text("Введите основную снасть:")
    return REGISTER_GEAR_MAIN


async def register_gear_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 5: Сохранение основной снасти."""
    context.user_data['gear_main'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел снасть: {context.user_data['gear_main']}")
    await update.message.reply_text("Расскажите о себе (кратко):")
    return REGISTER_BIO


async def register_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 6: Сохранение информации о себе."""
    context.user_data['bio'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел информацию о себе: {context.user_data['bio']}")
    await update.message.reply_text(    "📅 Введите вашу дату рождения в формате ДД.ММ.ГГГГ\n"
    "Пример: 15.05.1990")
    return REGISTER_BIRTH



async def register_birth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 6: Сохранение информации о себе."""
    context.user_data['birth_date'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел информацию о себе: {context.user_data['bio']}")

    try:
        birth_date = datetime.strptime(context.user_data['birth_date'], "%d.%m.%Y").date()
    except ValueError:
        await update.message.reply_text("❌ Неверный формат! Используйте ДД.ММ.ГГГГ")
        return REGISTER_BIRTH

    if birth_date > datetime.now().date():
        await update.message.reply_text("❌ Дата не может быть в будущем!")
        return REGISTER_BIRTH

    await update.message.reply_text("Введите вашу кличку:")
    return REGISTER_ALIAS



async def register_alias(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 7: Сохранение клички."""

    context.user_data['alias'] = update.message.text.strip()
    logger.info(f"Пользователь {update.effective_user.id} ввел кличку: {context.user_data['alias']}")
    await update.message.reply_text("Теперь отправьте фото профиля (необязательно):")
    return REGISTER_PHOTO


async def register_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, UserTgTable) -> int:
    """Шаг 8: Загрузка фото и сохранение данных в базу данных."""
    user = update.effective_user

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        # photo_path = f"{PHOTO_DIR}/{user.id}_profile.jpg"
        file_bytes = await photo_file.download_as_bytearray()
        object_name = f"avatars/{user.id}_profile.jpg"
        # await photo_file.download_to_drive(photo_path)
        minio_path = await upload_to_minio(file_bytes, object_name)
        print(minio_path)
        context.user_data[IMAGE_PATH_FIELD] = minio_path
        logger.info(f"Пользователь {user.id} загрузил фото.")
        await update.message.reply_text(MESSAGES["photo_updated"])
    else:
        context.user_data[IMAGE_PATH_FIELD] = "default.jpg"
        logger.info(f"Пользователь {user.id} пропустил загрузку фото.")
        await update.message.reply_text(MESSAGES["no_photo_sent"])

    # Сохраняем все данные в базу данных
    stmt = UserTgTable.insert().values(
        userid=user.id,
        username=user.username,
        first_name=context.user_data.get('first_name'),
        last_name=context.user_data.get('last_name'),
        phone_number=context.user_data.get('phone_number'),
        metod_catch=context.user_data.get('metod_catch'),
        gear_main=context.user_data.get('gear_main'),
        bio=context.user_data.get('bio'),
        birth_date=datetime.strptime(context.user_data['birth_date'], "%d.%m.%Y").date(),
        alias=context.user_data.get('alias'),
        image=context.user_data.get(IMAGE_PATH_FIELD)
    )



    with engine.connect() as conn:
        conn.execute(stmt)

        conn.commit()


    logger.info(f"Пользователь {user.id} успешно зарегистрирован.")
    await update.message.reply_text("Регистрация успешно завершена!",reply_markup=get_main_keyboard(True))
    
    return ConversationHandler.END


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена регистрации."""
    await update.message.reply_text(MESSAGES["edit_canceled"], reply_markup=None)
    logger.info(f"Пользователь {update.effective_user.id} отменил регистрацию.")
    await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(True))
    return ConversationHandler.END


# Диалог регистрации
register_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(register_button, pattern=f"^{CALLBACK_REGISTER}$")],  # Точка входа через Inline-кнопку "Регистрация"
    states={
        REGISTER_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_first_name)],
        REGISTER_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_last_name)],
        REGISTER_PHONE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone),
            MessageHandler(filters.Regex('^Отмена$'), cancel_registration)  # Отмена на любом шаге
        ],
        REGISTER_METOD_CATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_metod_catch)],
        REGISTER_GEAR_MAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_gear_main)],
        REGISTER_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_bio)],
        REGISTER_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_birth)],
        REGISTER_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_alias)],
        REGISTER_PHOTO: [
            MessageHandler(filters.PHOTO, lambda u, c: register_photo(u, c, UserTgTable)),
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: register_photo(u, c, UserTgTable))
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex('^Отмена$'), cancel_registration),  # Отмена через текст "Отмена"
        CallbackQueryHandler(cancel_registration, pattern=f"^{CALLBACK_CANCEL_EDIT}$")  # Отмена через Inline-кнопку
    ]
)