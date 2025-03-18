from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from sqlalchemy import delete
from db_connect import *
from value import *
from bot_minio import *
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик кнопки 'Удалить профиль'."""
    query = update.callback_query
    await query.answer()

    logger.info(f"Пользователь {query.from_user.id} нажал на кнопку 'Удалить профиль'.")
    await query.message.reply_text(
        "Вы уверены, что хотите удалить свой профиль? Это действие нельзя отменить.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да", callback_data=CALLBACK_CONFIRM_DELETE)],
            [InlineKeyboardButton("Нет", callback_data=CALLBACK_CANCEL_DELETE)]
        ])
    )
    return DELETE_CONFIRMATION


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE, UserTgTable) -> int:
    """Подтверждение удаления профиля."""
    query = update.callback_query
    await query.answer()

    user = query.from_user

    if query.data == CALLBACK_CONFIRM_DELETE:
        image = select(UserTgTable).where(UserTgTable.c.userid == user.id)
        stmt = UserTgTable.delete().where(UserTgTable.c[USER_ID_FIELD] == user.id)
        stmt2 = UserTable.delete().where(UserTable.c["username"] == f"tg_{user.id}")
        try:
            with engine.connect() as conn:
                result_image = conn.execute(image).fetchone()
                result = conn.execute(stmt)
                conn.execute(stmt2)
                conn.commit()


            if result_image.image:  # Проверяем наличие пути
                        success = await delete_from_minio(result_image.image)
                        if not success:
                            logger.error(f"Не удалось удалить файл из MinIO: {result_image.image}")

            if result.rowcount > 0:
                logger.info(f"Пользователь {user.id} успешно удалил свой профиль.")
                await query.message.reply_text(MESSAGES["profile_deleted"])
            else:
                logger.warning(f"Попытка удаления несуществующего профиля пользователем {user.id}.")
                await query.message.reply_text("Ошибка: Профиль не найден.")
        except Exception as e:
            logger.error(f"Ошибка при удалении профиля пользователя {user.id}: {e}")
            await query.message.reply_text("Произошла ошибка при удалении профиля. Попробуйте снова.")
    elif query.data == CALLBACK_CANCEL_DELETE:
        logger.info(f"Пользователь {user.id} отменил удаление профиля.")
        await query.message.reply_text(MESSAGES["deletion_canceled"])

    # Удаляем клавиатуру после действия
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning(f"Не удалось удалить клавиатуру: {e}")

    return ConversationHandler.END


# Диалог удаления профиля
delete_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(delete_profile, pattern=f"^{CALLBACK_DELETE_PROFILE}$")],
    states={
        DELETE_CONFIRMATION: [
            CallbackQueryHandler(lambda u, c: confirm_delete(u, c, UserTgTable), pattern=f"^{CALLBACK_CONFIRM_DELETE}|{CALLBACK_CANCEL_DELETE}$")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(lambda u, c: confirm_delete(u, c, UserTgTable), pattern=f"^{CALLBACK_CONFIRM_DELETE}|{CALLBACK_CANCEL_DELETE}$")
    ]
)