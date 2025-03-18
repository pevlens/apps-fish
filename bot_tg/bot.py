import logging
import asyncio
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    CallbackQuery
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes
)
from value import (
    REGISTER_FIRST_NAME, REGISTER_LAST_NAME, REGISTER_PHONE, REGISTER_METOD_CATCH,
    REGISTER_GEAR_MAIN, REGISTER_BIO, REGISTER_ALIAS, REGISTER_PHOTO,
    SELECT_FIELD, EDIT_FIRST_NAME, EDIT_LAST_NAME, EDIT_PHONE, EDIT_METOD_CATCH,
    EDIT_GEAR_MAIN, EDIT_BIO, EDIT_ALIAS, EDIT_PHOTO, DELETE_CONFIRMATION,
    CALLBACK_REGISTER, CALLBACK_SHOW_PROFILE, CALLBACK_EDIT_PROFILE, CALLBACK_DELETE_PROFILE,
    CALLBACK_CONFIRM_DELETE, CALLBACK_CANCEL_DELETE, CALLBACK_CANCEL_EDIT,TOKEN_TG_BOT,
    MESSAGES, USER_ID_FIELD, PHOTO_DIR
)
from db_connect import UserTgTable, engine
from bot_edit import edit_conv_handler
from bot_delete import *
from bot_ui import handle_button_press, get_main_keyboard
from bot_regist import register_conv_handler
from bot_send_channel import create_post_conv_handler
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



def user_exists(user_id: int) -> bool:
    """Проверяет, существует ли пользователь с указанным ID."""
    query = UserTgTable.select().where(UserTgTable.c[USER_ID_FIELD] == user_id)
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    logger.info(f"Проверка существования пользователя {user_id}: {result is not None}")
    return result is not None


async def handle_start_or_first_message(update: Update, context: ContextTypes.DEFAULT_TYPE, check_user_func) -> None:
    """Обработчик команды /start или первого сообщения пользователя."""
    user = update.effective_user
    is_registered = check_user_func(user.id)

    if is_registered:
        await update.message.reply_html(
            MESSAGES["start_registered"].format(first_name=user.first_name),
            reply_markup=get_main_keyboard(True)
        )
    else:
        await update.message.reply_html(
            MESSAGES["start_unregistered"].format(first_name=user.first_name),
            reply_markup=get_main_keyboard(False)
        )


def main():
    """Основная функция для запуска бота."""
    application = Application.builder().token(TOKEN_TG_BOT).build()

    # Регистрация обработчиков
    application.add_handler(register_conv_handler)

    application.add_handler(edit_conv_handler)
    application.add_handler(delete_conv_handler)
    application.add_handler(create_post_conv_handler)
    application.add_handler(CallbackQueryHandler(handle_button_press))
    
# Обработчики первого сообщения и /start
    application.add_handler(CommandHandler("start", lambda u, c: handle_start_or_first_message(u, c, user_exists)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: handle_start_or_first_message(u, c, user_exists)))

    logger.info("Бот запущен")
    # Запускаем бота; run_polling блокирует выполнение до остановки приложения.
    application.run_polling()


if __name__ == '__main__':
    main()
