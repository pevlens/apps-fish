from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from value import (
    REGISTER_FIRST_NAME, REGISTER_LAST_NAME, REGISTER_PHONE, REGISTER_METOD_CATCH,
    REGISTER_GEAR_MAIN, REGISTER_BIO, REGISTER_ALIAS, REGISTER_PHOTO,
    SELECT_FIELD, EDIT_FIRST_NAME, EDIT_LAST_NAME, EDIT_PHONE, EDIT_METOD_CATCH,
    EDIT_GEAR_MAIN, EDIT_BIO, EDIT_ALIAS, EDIT_PHOTO, DELETE_CONFIRMATION,
    CALLBACK_REGISTER, CALLBACK_SHOW_PROFILE, CALLBACK_EDIT_PROFILE, CALLBACK_DELETE_PROFILE,
    CALLBACK_CONFIRM_DELETE, CALLBACK_CANCEL_DELETE, CALLBACK_CANCEL_EDIT,
    MESSAGES,USER_ID_FIELD, CALLBACK_CREATE_POST,CALLBACK_EDIT_POST
)
from db_connect import UserTgTable
import logging
from db_connect import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_keyboard(user_exists: bool) -> InlineKeyboardMarkup:
    """Возвращает основную клавиатуру в зависимости от статуса пользователя."""
    if user_exists:
        keyboard = [
            [InlineKeyboardButton("💻 Показать профиль", callback_data=CALLBACK_SHOW_PROFILE)],
            [InlineKeyboardButton("📝 Изменить профиль", callback_data=CALLBACK_EDIT_PROFILE)],
            [InlineKeyboardButton("❌ Удалить профиль", callback_data=CALLBACK_DELETE_PROFILE)],
            [InlineKeyboardButton("➕ Создать пост", callback_data=CALLBACK_CREATE_POST)],
         
        ]
    else:
        keyboard = [[InlineKeyboardButton("✅ Регистрация", callback_data=CALLBACK_REGISTER)]]

    return InlineKeyboardMarkup(keyboard)

def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру для выбора поля при редактировании профиля."""
    keyboard = [
        [InlineKeyboardButton("Имя", callback_data="edit_first_name")],
        [InlineKeyboardButton("Фамилия", callback_data="edit_last_name")],
        [InlineKeyboardButton("Телефон", callback_data="edit_phone")],
        [InlineKeyboardButton("Метод ловли", callback_data="edit_metod_catch")],
        [InlineKeyboardButton("Снасть", callback_data="edit_gear_main")],
        [InlineKeyboardButton("О себе", callback_data="edit_bio")],
        [InlineKeyboardButton("Кличка", callback_data="edit_alias")],
        [InlineKeyboardButton("Фото", callback_data="edit_photo")],
        [InlineKeyboardButton("Отмена", callback_data=CALLBACK_CANCEL_EDIT)]
    ]
    return InlineKeyboardMarkup(keyboard)


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатий на inline-кнопки для регистрации, показа или удаления профиля.
    Обратите внимание: кнопка редактирования профиля (CALLBACK_EDIT_PROFILE) обрабатывается через ConversationHandler (bot_edit.py).
    """
    query: CallbackQuery = update.callback_query
    await query.answer()
    action = query.data
    if action == CALLBACK_REGISTER:
        await query.message.reply_text(MESSAGES["registration_started"], )
        return REGISTER_FIRST_NAME
    elif action == CALLBACK_SHOW_PROFILE:
        from bot_show import show_profile
        await show_profile(query, context, UserTgTable)
        return
    elif action == CALLBACK_DELETE_PROFILE:
        await query.message.reply_text(
            "Вы уверены, что хотите удалить свой профиль? Это действие нельзя отменить.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Да", callback_data=CALLBACK_CONFIRM_DELETE)],
                [InlineKeyboardButton("Нет", callback_data=CALLBACK_CANCEL_DELETE)]
            ])
        )
        return DELETE_CONFIRMATION
    # CALLBACK_EDIT_PROFILE обрабатывается через ConversationHandler в bot_edit.py.
