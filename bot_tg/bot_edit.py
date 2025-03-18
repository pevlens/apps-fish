from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from sqlalchemy import select, update
from value import (
    SELECT_FIELD, EDIT_FIRST_NAME, EDIT_LAST_NAME, EDIT_PHONE, EDIT_METOD_CATCH,
    EDIT_GEAR_MAIN, EDIT_BIO, EDIT_ALIAS, EDIT_PHOTO, EDIT_BIRTH,
    CALLBACK_CANCEL_EDIT, CALLBACK_EDIT_PROFILE, MESSAGES, USER_ID_FIELD, PHOTO_DIR
)
import os
import logging
from db_connect import UserTgTable, engine
from bot_ui import get_main_keyboard
from datetime import datetime
from bot_minio import *
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
keyboard_cancel = [[InlineKeyboardButton("❌ Отмена", callback_data=CALLBACK_CANCEL_EDIT)]]

# Словарь для сопоставления callback_data с состояниями редактирования
FIELD_TO_STATE_MAP = {
    "edit_first_name": EDIT_FIRST_NAME,
    "edit_last_name": EDIT_LAST_NAME,
    "edit_phone": EDIT_PHONE,
    "edit_metod_catch": EDIT_METOD_CATCH,
    "edit_gear_main": EDIT_GEAR_MAIN,
    "edit_bio": EDIT_BIO,
    "edit_alias": EDIT_ALIAS,
    "edit_photo": EDIT_PHOTO,
    "edit_birth":EDIT_BIRTH, 
}

async def edit_profile(message_or_query, context: ContextTypes.DEFAULT_TYPE, UserTgTable) -> int:
    """
    Обработчик начала редактирования профиля (entry point для ConversationHandler).
    Выводит текущие данные профиля и предлагает выбрать поле для редактирования.
    """
    if isinstance(message_or_query, CallbackQuery):
        user = message_or_query.from_user
        message = message_or_query.message
    else:
        user = message_or_query.effective_user
        message = message_or_query.message

    loading_message = await message.reply_text(MESSAGES["loading_message"], quote=False)

    query = select(UserTgTable).where(UserTgTable.c[USER_ID_FIELD] == user.id)
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()

    try:
        await loading_message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о загрузке: {e}")

    if result:
        profile_info = (
            f"<b>Ваш текущий профиль:</b>\n"
            f"Имя: {result.first_name}\n"
            f"Фамилия: {result.last_name}\n"
            f"Телефон: {result.phone_number or 'Не указан'}\n"
            f"Метод ловли: {result.metod_catch or 'Не указан'}\n"
            f"Снасть: {result.gear_main or 'Не указана'}\n"
            f"О себе: {result.bio or 'Не указано'}\n"
            f"Кличка: {result.alias or 'Не указана'}\n"
            f"Дата Рождения: {result.birth_date or 'Не указана'}\n"
        )
        await message.reply_html(profile_info)

        # Создаем клавиатуру для выбора поля редактирования
        keyboard = [
            [InlineKeyboardButton("Имя", callback_data="edit_first_name")],
            [InlineKeyboardButton("Фамилия", callback_data="edit_last_name")],
            [InlineKeyboardButton("Телефон", callback_data="edit_phone")],
            [InlineKeyboardButton("Метод ловли", callback_data="edit_metod_catch")],
            [InlineKeyboardButton("Снасть", callback_data="edit_gear_main")],
            [InlineKeyboardButton("О себе", callback_data="edit_bio")],
            [InlineKeyboardButton("Кличка", callback_data="edit_alias")],
            [InlineKeyboardButton("Фото", callback_data="edit_photo")],
            [InlineKeyboardButton("Дата Рождения", callback_data="edit_birth")],
            [InlineKeyboardButton("Отмена", callback_data=CALLBACK_CANCEL_EDIT)]
        ]
        await message.reply_text(
            MESSAGES["choose_field_to_edit"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECT_FIELD
    else:
        await message.reply_text("Ошибка: Профиль не найден.")
        return ConversationHandler.END

async def handle_select_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обработка выбора поля для редактирования.
    После выбора пользователю отправляется запрос на ввод нового значения.
    """
    query: CallbackQuery = update.callback_query
    await query.answer()
    action = query.data
    logger.info(f"Пользователь {query.from_user.id} выбрал действие: {action}")
    
    if action in FIELD_TO_STATE_MAP:
        field_name = action.replace("edit_", "").capitalize()
        logger.info(f"Переход к состоянию: {FIELD_TO_STATE_MAP[action]}")
        await query.message.reply_text(f"Введите новое значение для {field_name} или напишите 'Отмена' для отмены:", reply_markup=InlineKeyboardMarkup(keyboard_cancel))
        return FIELD_TO_STATE_MAP[action]
    elif action == CALLBACK_CANCEL_EDIT:
        logger.info(f"Пользователь {query.from_user.id} отменил редактирование.")
        await query.message.reply_text(MESSAGES["edit_canceled"], reply_markup=None)
        return ConversationHandler.END
    else:
        logger.error(f"Неизвестное действие при редактировании: {action}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")
        return ConversationHandler.END

async def update_field(update: Update, context: ContextTypes.DEFAULT_TYPE, UserTgTable, field: str) -> int:
    user = update.effective_user
    new_value = update.message.text.strip()
    if  field == "birth_date":
       
        try:
            new_value = datetime.strptime(new_value, "%d.%m.%Y").date()
            logger.info(f"Пользователь {user.id} пытается обновить поле {field} на '{new_value}'  обьект {type(new_value)}.")
            stmt = UserTgTable.update().where(UserTgTable.c.userid == user.id).values({field: new_value})

        except ValueError:
            await update.message.reply_text("❌ Неверный формат! Используйте ДД.ММ.ГГГГ")
            return EDIT_BIRTH

        if new_value > datetime.now().date():
            await update.message.reply_text("❌ Дата не может быть в будущем!")
            return EDIT_BIRTH

    else:
        logger.info(f"Пользователь {user.id} пытается обновить поле {field} на '{new_value}'.")
        stmt = UserTgTable.update().where(UserTgTable.c[USER_ID_FIELD] == user.id).values({field: new_value})
    try:
        stmt2 = UserTgTable.update().where(UserTgTable.c[USER_ID_FIELD] == user.id).values({"profile_change": True})
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.execute(stmt2)
            conn.commit()

        if result.rowcount > 0:
            logger.info(f"Пользователь {user.id} успешно обновил поле {field} на '{new_value}'.")
            await update.message.reply_text(
                MESSAGES["field_updated"].format(field=field.capitalize(), new_value=new_value)
            )
        else:
            logger.warning(f"Попытка обновления несуществующего профиля пользователем {user.id}.")
            await update.message.reply_text("Ошибка: Профиль не найден.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении данных пользователя {user.id}: {e}")
        await update.message.reply_text("Произошла ошибка при обновлении данных. Попробуйте снова.")

    # После завершения действия отправляем главное меню
    await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(True))
    return ConversationHandler.END

async def edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, UserTgTable) -> int:
    """
    Обновление фото профиля.
    При получении фото бот сохраняет его и обновляет информацию в базе данных.
    """
    user = update.effective_user

    if update.message.photo:
        try:    
            photo_file = await update.message.photo[-1].get_file()
            file_bytes = await photo_file.download_as_bytearray()
            object_name = f"avatars/{user.id}_profile.jpg"
            minio_path = await upload_to_minio(file_bytes, object_name)



            # photo_path = f"{PHOTO_DIR}/{user.id}_profile.jpg"
            # await photo_file.download_to_drive(photo_path)

            stmt = UserTgTable.update().where(UserTgTable.c[USER_ID_FIELD] == user.id).values(
                {'image': minio_path}
            )
            with engine.connect() as conn:
                result = conn.execute(stmt)
                conn.commit()

            if result.rowcount > 0:
                await update.message.reply_text(MESSAGES["photo_updated"])
                logger.info(f"Пользователь {user.id} обновил фото профиля.")
            else:
                await update.message.reply_text("Ошибка: Профиль не найден.")
                logger.warning(f"Попытка обновления фото несуществующего профиля пользователем {user.id}.")

        except Exception as e:
            logger.error(f"Ошибка обновления фото: {str(e)}")
            await update.message.reply_text("Произошла ошибка при обновлении фото. Попробуйте ещё раз.")
    else:
        await update.message.reply_text(MESSAGES["no_photo_sent"])
    await update.message.reply_text("Главное меню:", reply_markup=get_main_keyboard(True))
    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # await update.message.reply_text(MESSAGES["edit_canceled"], reply_markup=None)
    # logger.info(f"Пользователь {update.effective_user.id} отменил редактирование профиля.")
    # # После отмены также показываем главное меню
    
    # return ConversationHandler.END
    try:
        # Получаем сообщение из любого источника
        message = update.effective_message
        
        if message:
            await message.reply_text(
                MESSAGES["edit_canceled"],
                reply_markup=get_main_keyboard(True)
            )
        else:
            # Если сообщение недоступно, отправляем через контекст
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=MESSAGES["edit_canceled"],
                reply_markup=get_main_keyboard(True)
            )

        logger.info(f"Пользователь {update.effective_user.id} отменил редактирование")
        
    except Exception as e:
        logger.error(f"Ошибка при отмене: {str(e)}")
        
    finally:
        # Всегда очищаем данные пользователя
        context.user_data.clear()
        
        # Возвращаемся в главное меню
        # await show_main_menu(update, context)  # Раскомментировать если есть меню
        
        return ConversationHandler.END

# Диалог редактирования профиля через ConversationHandler
edit_conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            lambda update, context: edit_profile(update.callback_query, context, UserTgTable),
            pattern=f"^{CALLBACK_EDIT_PROFILE}$"
        )
    ],
    states={
        SELECT_FIELD: [CallbackQueryHandler(handle_select_field)],
        EDIT_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'first_name'))],
        EDIT_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'last_name'))],
        EDIT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'phone_number'))],
        EDIT_METOD_CATCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'metod_catch'))],
        EDIT_GEAR_MAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'gear_main'))],
        EDIT_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'bio'))],
        EDIT_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'birth_date'))],
        EDIT_ALIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: update_field(u, c, UserTgTable, 'alias'))],
        EDIT_PHOTO: [
            MessageHandler(filters.PHOTO, lambda u, c: edit_photo(u, c, UserTgTable)),
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: edit_photo(u, c, UserTgTable))
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex('^Отмена$'), cancel_edit),
        CallbackQueryHandler(cancel_edit, pattern=f"^{CALLBACK_CANCEL_EDIT}$")
    ]
)
