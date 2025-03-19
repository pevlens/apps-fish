
import os
from dotenv import load_dotenv

load_dotenv(os.getenv('VAULT_SECRETS_FILE', '.env'))

TOKEN_TG_BOT = os.getenv('TOKEN_TG_BOT', 'default-key')
#DATABASE_URL = os.getenv('DATABASE_URL', 'default-url')
#TOKEN_TG_BOT = '7890053954:AAGyobNwIaYH0TRt0asZlmHiB2eN25oOczM'
#DATABASE_URL = 'sqlite:////home/admin/exemple_job/back_for_yarik/fishltf/db.sqlite3'
DB_USER = os.getenv('DATABASE_USER', 'default-user')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD', 'default-user')
DB_HOST = os.getenv('DATABASE_HOST', 'default-user')
DB_PORT = os.getenv('DATABASE_PORT', 'default-user')
DB_NAME = os.getenv('DATABASE_NAME', 'default-user')
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Состояния для диалога регистрации
#REGISTER_FIRST_NAME, REGISTER_LAST_NAME, REGISTER_PHONE, REGISTER_METOD_CATCH, REGISTER_GEAR_MAIN, REGISTER_BIO, REGISTER_ALIAS = range(7)



# Состояния для регистрации
(
    REGISTER_FIRST_NAME,
    REGISTER_LAST_NAME,
    REGISTER_PHONE,
    REGISTER_METOD_CATCH,
    REGISTER_GEAR_MAIN,
    REGISTER_BIO,
    REGISTER_ALIAS,
    REGISTER_PHOTO,
    REGISTER_BIRTH,
) = range(9)

# Состояния для редактирования профиля
(
    SELECT_FIELD,
    EDIT_FIRST_NAME,
    EDIT_LAST_NAME,
    EDIT_PHONE,
    EDIT_METOD_CATCH,
    EDIT_GEAR_MAIN,
    EDIT_BIO,
    EDIT_ALIAS,
    EDIT_PHOTO,
    EDIT_BIRTH,
) = range(9, 19)


# Состояния для создания поста
(
    CREATE_POST_START,
    CREATE_POST_ABOUT,
    CREATE_POST_WEIGHT,
    CREATE_POST_BAIT,
    CREATE_POST_LOCATION,
    CREATE_POST_FISH,
    CREATE_POST_IMAGE,
) = range(18, 25)


# Состояния для редактирования поста
(
    EDIT_POST_START,
    EDIT_POST_ABOUT,
    EDIT_POST_WEIGHT,
    EDIT_POST_BAIT,
    EDIT_POST_LOCATION,
    EDIT_POST_FISH,
    EDIT_POST_IMAGE,
) = range(25, 32)

# Состояние для удаления профиля
DELETE_CONFIRMATION = 10

# Название таблицы в базе данных

# Путь к папке для сохранения фото
PHOTO_DIR = 'tg'

# Поле для хранения ID пользователя
USER_ID_FIELD = 'userid'

# Поле для хранения пути к фото
IMAGE_PATH_FIELD = 'image'

#CHANNEL_ID = "-1002417134914"
CHANNEL_ID = os.getenv('CHANNEL_ID', 'default-url')

# Все возможные callback_data для Inline-кнопок
CALLBACK_REGISTER = "register"
CALLBACK_SHOW_PROFILE = "show_profile"
CALLBACK_EDIT_PROFILE = "edit_profile"
CALLBACK_DELETE_PROFILE = "delete_profile"
CALLBACK_CONFIRM_DELETE = "confirm_delete"
CALLBACK_CANCEL_DELETE = "cancel_delete"
CALLBACK_CANCEL_EDIT = "cancel_edit"
CALLBACK_CREATE_POST  = "create_post"
CALLBACK_CANCEL_POST  = "cancel_post"
CALLBACK_EDIT_POST = "edit_post"
CALLBACK_CANCEL_EDIT_POST = "cancel_edit_post"

# Сообщения бота
MESSAGES = {
    "start_registered": "<b>Привет, {first_name}!</b>\n\nВы уже зарегистрированы! Выберите действие:",
    "start_unregistered": "<b>Привет, {first_name}!</b>\n\nДобро пожаловать! Для использования бота необходимо зарегистироваться.",
    "registration_started": "Начинаем регистрацию. Введите ваше имя:",
    "field_updated": "{field} успешно обновлен на '{new_value}'.",
    "photo_updated": "Фото успешно обновлено!",
    "no_photo_sent": "Вы не отправили фото. Фото не изменено.",
    "profile_deleted": "Ваш профиль успешно удален.",
    "deletion_canceled": "Удаление профиля отменено.",
    "edit_canceled": "Редактирование профиля отменено.",
    "loading_message": "Загрузка вашего профиля...",
    "choose_field_to_edit": "Выберите поле для изменения:",
    "create_post_started": "Начинаем создание поста...",
    "post_sent_to_channel": "Ваш пост успешно отправлен в канал!",
    "edit_post_started": "Начинаем редактирование вашего последнего поста...",
    "post_field_updated": "{field} успешно обновлен!",
    "no_posts_found": "Ошибка: У вас нет постов для редактирования.",
    "photo_updated": "Фото успешно обновлено!",
    "edit_post_canceled": "Редактирование поста отменено.",
}

# Экспорт всех значений
__all__ = [
    "REGISTER_FIRST_NAME", "REGISTER_LAST_NAME", "REGISTER_PHONE", "REGISTER_METOD_CATCH", "REGISTER_BIRTH",
    "REGISTER_GEAR_MAIN", "REGISTER_BIO", "REGISTER_ALIAS", "REGISTER_PHOTO",
    "SELECT_FIELD", "EDIT_FIRST_NAME", "EDIT_LAST_NAME", "EDIT_PHONE", "EDIT_METOD_CATCH", "EDIT_BIRTH",
    "EDIT_GEAR_MAIN", "EDIT_BIO", "EDIT_ALIAS", "EDIT_PHOTO",
    "DELETE_CONFIRMATION",
    "PHOTO_DIR", "USER_ID_FIELD", "IMAGE_PATH_FIELD",
    "CALLBACK_REGISTER", "CALLBACK_SHOW_PROFILE", "CALLBACK_EDIT_PROFILE", "CALLBACK_DELETE_PROFILE",
    "CALLBACK_CONFIRM_DELETE", "CALLBACK_CANCEL_DELETE", "CALLBACK_CANCEL_EDIT",
    "MESSAGES", "TOKEN_TG_BOT", "DATABASE_URL",    "CREATE_POST_START",
    "CREATE_POST_ABOUT",
    "CREATE_POST_WEIGHT",
    "CREATE_POST_BAIT",
    "CREATE_POST_LOCATION",
    "CREATE_POST_FISH",
    "CREATE_POST_IMAGE",
    "CALLBACK_CREATE_POST", 
    "CALLBACK_CANCEL_POST",
    "CHANNEL_ID",
    "EDIT_POST_START",
    "EDIT_POST_ABOUT",
    "EDIT_POST_WEIGHT",
    "EDIT_POST_BAIT",
    "EDIT_POST_LOCATION",
    "EDIT_POST_FISH",
    "EDIT_POST_IMAGE",
    "CALLBACK_EDIT_POST",
    "CALLBACK_CANCEL_EDIT_POST"
]