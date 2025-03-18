from telegram import Update, CallbackQuery
from telegram.ext import MessageHandler, filters, ContextTypes
from sqlalchemy import select
from db_connect import *
import os
import io
from bot_minio import *
from bot_ui import get_main_keyboard
async def show_profile(message_or_query, context: ContextTypes.DEFAULT_TYPE, UserTgTable) -> None:
    """Обработчик показа профиля."""
    if isinstance(message_or_query, CallbackQuery):
        user = message_or_query.from_user
        message = message_or_query.message
    else:
        user = message_or_query.effective_user
        message = message_or_query.message

    query = select(UserTgTable).where(UserTgTable.c.userid == user.id)
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()

    if result:
        profile_info = (
            f"<b>Ваш профиль:</b>\n"
            f"Имя: {result.first_name}\n"
            f"Фамилия: {result.last_name}\n"
            f"Username: {result.username or 'Не указан'}\n"
            f"Телефон: {result.phone_number or 'Не указан'}\n"
            f"Метод ловли: {result.metod_catch or 'Не указан'}\n"
            f"Снасть: {result.gear_main or 'Не указана'}\n"
            f"О себе: {result.bio or 'Не указано'}\n"
            f"Кличка: {result.alias or 'Не указана'}\n"
            f"Дата рождения: {result.birth_date.strftime('%Y-%m-%d') or 'Не указана' }\n"
            f"Дата регистрации: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        if result.image:
            minio_path = result.image
            response = minio_client.get_object(BUCKET_NAME, minio_path)
            image_data = io.BytesIO(response.data)
            image_data.seek(0)
            if image_data:

                await message.reply_photo(photo=image_data, caption=profile_info, parse_mode="HTML", reply_markup=get_main_keyboard(True))
            # full_path = os.path.join(result.image)
            # if os.path.exists(full_path):
            #     with open(full_path, 'rb') as photo_file:
            #         await message.reply_photo(photo=photo_file, caption=profile_info, parse_mode="HTML", reply_markup=get_main_keyboard(True))

            else:
                await message.reply_html(profile_info + "\n\n(Фото недоступно)", reply_markup=get_main_keyboard(True))
        else:
            await message.reply_html(profile_info, reply_markup=get_main_keyboard(True))
    else:
        await message.reply_text("Ошибка: Профиль не найден.", reply_markup=get_main_keyboard(True))