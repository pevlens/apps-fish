from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from sqlalchemy import delete,inspect
from sqlalchemy.exc import SQLAlchemyError
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

    user_id = user.id
    if query.data == CALLBACK_CONFIRM_DELETE:
            
        # image = select(UserTgTable).where(UserTgTable.c.userid == user.id)
        # stmt = UserTgTable.delete().where(UserTgTable.c[USER_ID_FIELD] == user.id)
        # stmt2 = UserTable.delete().where(UserTable.c["username"] == f"tg_{user.id}")
        try:
            async with engine.begin() as conn:
                # 1. Удаление изображения из MinIO
                image_result = await conn.execute(
                    select(UserTgTable.c.image).where(UserTgTable.c.userid == user_id))
                image_data = image_result.scalar()
                if image_data:
                    success = await delete_from_minio(image_data)
                    if not success:
                        logger.error(f"Не удалось удалить файл из MinIO: {image_data}")
                
                # 2. Автоматическое определение всех зависимостей
                inspector = inspect(engine)
                dependencies = set()

                # Собираем связанные таблицы для auth_user и manageappfish_usertg
                for target_table in ['auth_user', 'manageappfish_usertg']:
                    for table_name in inspector.get_table_names():
                        for fk in inspector.get_foreign_keys(table_name):
                            if fk['referred_table'] == target_table:
                                dependencies.add((
                                    table_name,
                                    fk['constrained_columns'],
                                    target_table
                                ))

                # 3. Удаление данных из зависимых таблиц
                processed_tables = set()
                for table_info in dependencies:
                    table_name, columns, ref_table = table_info
                    if table_name in processed_tables:
                        continue

                    try:
                        tbl = Table(table_name, metadata, autoload_with=engine)
                        
                        # Определяем условие удаления
                        for col in columns:
                            if ref_table == 'auth_user':
                                # Для связи с auth_user используем username
                                condition = (getattr(tbl.c, col) == f"tg_{user_id}")
                            else:
                                # Для других связей используем user_id
                                condition = (getattr(tbl.c, col) == user_id)
                            
                            await conn.execute(tbl.delete().where(condition))
                            processed_tables.add(table_name)
                            break  # Обработали одну связь для таблицы

                    except Exception as e:
                        logger.error(f"Ошибка при удалении из {table_name}: {e}")

               # 4. Удаление основных записей
                await conn.execute(UserTgTable.delete().where(UserTgTable.c.userid == user_id))
                result = await conn.execute(
                    UserTable.delete().where(UserTable.c.username == f"tg_{user_id}")
                )

                if result.rowcount > 0:
                    logger.info(f"Пользователь {user_id} успешно удалён")
                    await query.message.reply_text(MESSAGES["profile_deleted"])
                else:
                    logger.warning(f"Попытка удаления несуществующего профиля: {user_id}")
                    await query.message.reply_text("Ошибка: Профиль не найден")


        #     with engine.connect() as conn:
        #         result_image = conn.execute(image).fetchone()
        #         result = conn.execute(stmt)
        #         conn.execute(stmt2)
        #         conn.commit()


            # if result_image.image:  # Проверяем наличие пути
            #             success = await delete_from_minio(result_image.image)
            #             if not success:
            #                 logger.error(f"Не удалось удалить файл из MinIO: {result_image.image}")

            # if result.rowcount > 0:
            #     logger.info(f"Пользователь {user.id} успешно удалил свой профиль.")
            #     await query.message.reply_text(MESSAGES["profile_deleted"])
            # else:
            #     logger.warning(f"Попытка удаления несуществующего профиля пользователем {user.id}.")
            #     await query.message.reply_text("Ошибка: Профиль не найден.")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных: {e}")

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