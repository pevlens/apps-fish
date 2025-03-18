from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from sqlalchemy import select, update
from value import (
    EDIT_POST_START, EDIT_POST_ABOUT, EDIT_POST_WEIGHT, EDIT_POST_BAIT,
    EDIT_POST_LOCATION, EDIT_POST_FISH, EDIT_POST_IMAGE, CALLBACK_EDIT_POST,
    CALLBACK_CANCEL_EDIT_POST, MESSAGES, USER_ID_FIELD, IMAGE_PATH_FIELD
)
import os
import logging
from db_connect import *
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)





async def edit_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса редактирования поста через Inline-кнопку."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    message = query.message
    id_user = get_user_id_by_userid(user.id)
    # Запрашиваем последний пост пользователя из базы данных
    stmt = CatchTgTable.select().where(CatchTgTable.c.user_id == id_user).order_by(CatchTgTable.c.created_at.desc()).limit(1)
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchone()

    if not result:
        logger.warning(f"Пользователь {user.id} не имеет постов для редактирования.")
        await message.reply_text("Ошибка: У вас нет постов для редактирования.")
        return ConversationHandler.END

    # Сохраняем ID поста в контексте
    context.user_data['post_id'] = result.id

    # Отображаем текущие данные поста
    post_info = (
        f"<b>Текущий пост:</b>\n"
        f"Описание: {result.about or 'Не указано'}\n"
        f"Вес: {result.weight or 'Не указан'} грамм\n"
        f"Приманка: {result.bait or 'Не указана'}\n"
        f"Локация: {result.location_name or 'Не указана'}\n"
        f"Рыба: {result.fish or 'Не указана'}\n"
    )
    await message.reply_html(post_info)

    # Показываем клавиатуру для выбора поля для редактирования
    keyboard = [
        [InlineKeyboardButton("Описание", callback_data="edit_post_about")],
        [InlineKeyboardButton("Вес", callback_data="edit_post_weight")],
        [InlineKeyboardButton("Приманка", callback_data="edit_post_bait")],
        [InlineKeyboardButton("Локация", callback_data="edit_post_location")],
        [InlineKeyboardButton("Рыба", callback_data="edit_post_fish")],
        [InlineKeyboardButton("Фото", callback_data="edit_post_image")],
        [InlineKeyboardButton("Отмена", callback_data=CALLBACK_CANCEL_EDIT_POST)]
    ]
    await message.reply_text(
        "Выберите поле для редактирования:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EDIT_POST_START


async def handle_edit_post_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора поля для редактирования поста."""
    query = update.callback_query
    await query.answer()

    action = query.data
    logger.info(f"Пользователь {query.from_user.id} выбрал поле для редактирования: {action}")

    field_map = {
        "edit_post_about": ("Описание", EDIT_POST_ABOUT),
        "edit_post_weight": ("Вес", EDIT_POST_WEIGHT),
        "edit_post_bait": ("Приманка", EDIT_POST_BAIT),
        "edit_post_location": ("Локация", EDIT_POST_LOCATION),
        "edit_post_fish": ("Рыба", EDIT_POST_FISH),
        "edit_post_image": ("Фото", EDIT_POST_IMAGE),
    }

    if action in field_map:
        field_name, next_state = field_map[action]
        await query.message.reply_text(f"Введите новое значение для {field_name}:")
        return next_state
    elif action == CALLBACK_CANCEL_EDIT_POST:
        await query.message.reply_text("Редактирование поста отменено.", reply_markup=None)
        return ConversationHandler.END
    else:
        logger.error(f"Неизвестное действие при редактировании поста: {action}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END


async def update_post_field(update: Update, context: ContextTypes.DEFAULT_TYPE, CatchTgTable, field: str) -> int:
    """Обновление выбранного поля поста."""
    user = update.effective_user
    new_value = update.message.text.strip()

    if not new_value and field != IMAGE_PATH_FIELD:  # Для фото пустое значение допустимо
        await update.message.reply_text(f"Вы не ввели значение для {field}. Пожалуйста, попробуйте снова:")
        return getattr(context, f"EDIT_POST_{field.upper()}")

    post_id = context.user_data.get('post_id')
    if not post_id:
        logger.warning(f"Пользователь {user.id} пытается редактировать пост, но ID поста не найден.")
        await update.message.reply_text("Ошибка: Пост не найден.")
        return ConversationHandler.END

    stmt = CatchTgTable.update().where(CatchTgTable.c.id == post_id).values({field: new_value})
    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

        if result.rowcount > 0:
            logger.info(f"Пользователь {user.id} успешно обновил поле {field} поста с ID {post_id}.")
            await update.message.reply_text(f"{field.capitalize()} успешно обновлен!")
        else:
            logger.warning(f"Пользователь {user.id} не смог обновить поле {field} поста с ID {post_id}.")
            await update.message.reply_text("Ошибка: Пост не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении поста пользователя {user.id}: {e}")
        await update.message.reply_text("Произошла ошибка при обновлении поста. Попробуйте снова.")
        return ConversationHandler.END

    return ConversationHandler.END


async def edit_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обновление фото поста."""
    user = update.effective_user
    post_id = context.user_data.get('post_id')

    if not post_id:
        logger.warning(f"Пользователь {user.id} пытается обновить фото поста, но ID поста не найден.")
        await update.message.reply_text("Ошибка: Пост не найден.")
        return ConversationHandler.END

    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"tg/{user.id}_post_{post_id}.jpg"
        await photo_file.download_to_drive(photo_path)

        stmt = CatchTgTable.update().where(CatchTgTable.c.id == post_id).values(image=photo_path)
        try:
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

            if result.rowcount > 0:
                logger.info(f"Пользователь {user.id} успешно обновил фото поста с ID {post_id}.")
                await update.message.reply_text("Фото успешно обновлено!")
            else:
                logger.warning(f"Пользователь {user.id} не смог обновить фото поста с ID {post_id}.")
                await update.message.reply_text("Ошибка: Пост не найден.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении фото поста пользователя {user.id}: {e}")
            await update.message.reply_text("Произошла ошибка при обновлении фото. Попробуйте снова.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Вы не отправили новое фото. Фото не изменено.")

    return ConversationHandler.END


async def cancel_edit_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена редактирования поста."""
    await update.message.reply_text("Редактирование поста отменено.", reply_markup=None)
    logger.info(f"Пользователь {update.effective_user.id} отменил редактирование поста.")
    return ConversationHandler.END


# Диалог редактирования поста
edit_post_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_post_button, pattern=f"^{CALLBACK_EDIT_POST}$")],
    states={
        EDIT_POST_START: [CallbackQueryHandler(handle_edit_post_field)],  # Выбор поля для редактирования
        EDIT_POST_ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_post_field(u, c, CatchTgTable, 'about'))],
        EDIT_POST_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_post_field(u, c, CatchTgTable, 'weight'))],
        EDIT_POST_BAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_post_field(u, c, CatchTgTable, 'bait'))],
        EDIT_POST_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_post_field(u, c, CatchTgTable, 'location_name'))],
        EDIT_POST_FISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_post_field(u, c, CatchTgTable, 'fish'))],
        EDIT_POST_IMAGE: [
            MessageHandler(filters.PHOTO, lambda u, c: edit_post_image(u, c, CatchTgTable)),
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: edit_post_image(u, c, CatchTgTable))
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex('^Отмена$'), cancel_edit_post),  # Отмена через текст "Отмена"
        CallbackQueryHandler(cancel_edit_post, pattern=f"^{CALLBACK_CANCEL_EDIT_POST}$")  # Отмена через Inline-кнопку
    ]
)