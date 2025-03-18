from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
from sqlalchemy import insert
from datetime import datetime
from value import (
    CREATE_POST_START, CREATE_POST_ABOUT, CREATE_POST_WEIGHT, CREATE_POST_BAIT,
    CREATE_POST_LOCATION, CREATE_POST_FISH, CREATE_POST_IMAGE, MESSAGES,
    CALLBACK_CREATE_POST, CALLBACK_CANCEL_POST,CHANNEL_ID
)
import asyncio
import os
import io
from telegram import InputMediaPhoto
import logging
from db_connect import *
from bot_ui import *
from bot_hash import *
from bot_minio import *
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data=CALLBACK_CANCEL_POST)]]



CREATE_POST_IMAGE = 6

async def process_media_group(
    media_group_id: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    CatchTgTable,
    CatchTgImage,
    UserTgTable
):
    """Обработчик медиагруппы: сохраняет пост после сбора всех фото."""
    # Даем время на получение всех фото (2-5 сек)
    await asyncio.sleep(5)

    # Достаем группу из контекста
    media_group = context.user_data["media_groups"].get(media_group_id, {})
    if not media_group:
        return

    user = update.effective_user
    user_id = get_user_id_by_userid(user.id)

    try:
        with engine.connect() as conn:
            # Сохраняем пост
            stmt = CatchTgTable.insert().values(
                user_id=user_id,
                about=context.user_data.get('about'),
                weight=context.user_data.get('weight'),
                bait=context.user_data.get('bait'),
                location_name=context.user_data.get('location_name'),
                fish=context.user_data.get('fish'),
            )
            result = conn.execute(stmt)
            conn.commit()
            new_post_id = result.inserted_primary_key[0]
            context.user_data["id"] = new_post_id
            # Сохраняем фото группы
            for photo in media_group["photos"]:
                stmt_img = CatchTgImage.insert().values(
                    cacthtg_id=new_post_id,
                    image=photo["path"],
                    image_hash=photo["hash"]
                )
                conn.execute(stmt_img)
            conn.commit()

        # Отправляем пост в канал (только для медиагруппы)
        await update.message.reply_text("Фото добавлено в группу.")
        await send_post_to_channel(update, context, CatchTgTable, UserTgTable, CatchTgImage)

        

    except Exception as e:
        logger.error(f"Ошибка в медиагруппе: {e}")
        await update.message.reply_text("Ошибка при обработке группы фото.")
    finally:
        # Удаляем группу из контекста
        if media_group_id in context.user_data["media_groups"]:
            del context.user_data["media_groups"][media_group_id]

    # return ConversationHandler.END



async def create_post_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса создания поста через Inline-кнопку."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    message = query.message
    loading_message = await message.reply_text(MESSAGES["loading_message"], quote=False)
    logger.info(f"Пользователь {user.id} начал создание поста.")
   # await message.reply_text("Начинаем создание поста. Введите описание(Опишите как словили в какое время. то что вы считаете нужным):", reply_markup=ReplyKeyboardRemove())
    try:
        await loading_message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение о загрузке: {e}")

    # Показываем клавиатуру с кнопкой "Отмена"
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data=CALLBACK_CANCEL_POST)]]
    await message.reply_text(
        "Начинаем создание поста. Введите описание(Опишите как словили в какое время. то что вы считаете нужным):\n\n(Для отмены нажмите кнопку ниже)",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CREATE_POST_ABOUT


async def create_post_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 1: Сохранение описания."""
    user = update.effective_user
    #new_value = update.message.text.strip()
    

    if update.message:
        new_value = update.message.text.strip()
    elif update.callback_query:
        new_value = None
        await cancel_create_post(update, context)
        return ConversationHandler.END
    else:
        logger.warning(f"Неизвестный тип обновления при вводе описания для пользователя {user.id}.")
        return ConversationHandler.END


    if new_value and new_value.lower() == "отмена":
        await cancel_create_post(update, context)
        return ConversationHandler.END

    if not new_value:
        await update.message.reply_text("Вы не ввели описание(оно обязательно, краткую информацию). Пожалуйста, попробуйте снова:")
        return CREATE_POST_ABOUT

    context.user_data['about'] = new_value
    logger.info(f"Пользователь {user.id} ввел описание: {new_value}")


    await update.message.reply_text("Введите суммарный вес пойманной рыбы (в граммах):",reply_markup=InlineKeyboardMarkup(keyboard))
    return CREATE_POST_WEIGHT


async def create_post_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 2: Сохранение веса рыбы."""
    user = update.effective_user
    weight_input = update.message.text.strip()

    # Проверяем, что введено число
    if not weight_input.isdigit():
        await update.message.reply_text("Вес должен быть числом. Пожалуйста, введите вес снова:", reply_markup=InlineKeyboardMarkup(keyboard))
        return CREATE_POST_WEIGHT

    context.user_data['weight'] = int(weight_input)
    logger.info(f"Пользователь {user.id} ввел вес: {weight_input} грамм.")
    await update.message.reply_text("Введите название приманки(необезательно):", reply_markup=InlineKeyboardMarkup(keyboard))
    return CREATE_POST_BAIT


async def create_post_bait(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 3: Сохранение приманки."""
    user = update.effective_user
    new_value = update.message.text.strip()

    if not new_value:
        new_value = "не указанно"
        # await update.message.reply_text("Вы не ввели название приманки. Пожалуйста, попробуйте снова:")
        # return CREATE_POST_BAIT

    context.user_data['bait'] = new_value
    logger.info(f"Пользователь {user.id} ввел приманку: {new_value}")
    await update.message.reply_text("Введите название локации, где была поймана рыба(наименовиние и в каком регеоне находится 'oз. Погост Пинский р-н.'):",reply_markup=InlineKeyboardMarkup(keyboard))
    return CREATE_POST_LOCATION


async def create_post_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 4: Сохранение локации."""
    user = update.effective_user
    new_value = update.message.text.strip()

    if not new_value:
        new_value = "не указанно"
        # await update.message.reply_text("Вы не ввели название локации. Пожалуйста, попробуйте снова:")
        # return CREATE_POST_LOCATION

    context.user_data['location_name'] = new_value
    logger.info(f"Пользователь {user.id} ввел локацию: {new_value}")
    await update.message.reply_text("Введите название пойманных рыб(обязательнное поле):",reply_markup=InlineKeyboardMarkup(keyboard))
    return CREATE_POST_FISH


async def create_post_fish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Шаг 5: Сохранение названия рыбы."""
    user = update.effective_user
    new_value = update.message.text.strip()

    if not new_value:
        await update.message.reply_text("Вы не ввели название рыб. Пожалуйста, попробуйте снова:",reply_markup=InlineKeyboardMarkup(keyboard))
        return CREATE_POST_FISH

    context.user_data['fish'] = new_value
    logger.info(f"Пользователь {user.id} ввел название рыбы: {new_value}")
    await update.message.reply_text("Теперь отправьте фото пойманной рыбы (обязательное поле) :",reply_markup=InlineKeyboardMarkup(keyboard))
    return CREATE_POST_IMAGE


async def create_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE, CatchTgTable, UserTgTable, CatchTgImage) -> int:
    """Шаг 6: Загрузка фото и сохранение данных в базу данных."""
    user = update.effective_user




    if update.message and update.message.photo:
        if update.message.media_group_id:
            # Обработка медиагруппы
            media_group_id = update.message.media_group_id

            # Инициализация группы, если ее нет
            context.user_data.setdefault("media_groups", {})
            if media_group_id not in context.user_data["media_groups"]:
                context.user_data["media_groups"][media_group_id] = {
                    "photos": [],
                    "task_created": False  # Флаг для отслеживания задачи
                }

            current_group = context.user_data["media_groups"][media_group_id]

            # Скачивание фото
            photo_file = await update.message.photo[-1].get_file()
            file_bytes = await photo_file.download_as_bytearray()
            #photo_path = f"tg/{user.id}_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')}.jpg"
            object_name = f"tg/{user.id}_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')}.jpg"
            minio_path = await upload_to_minio(file_bytes, object_name)

            #await photo_file.download_to_drive(photo_path)
            #image_hash = calculate_image_hash(photo_path)
            if minio_path:
                # Вычисляем хеш из байтов без сохранения на диск
                image_hash = calculate_image_hash(file_bytes)

            # Добавляем фото в группу
            current_group["photos"].append({"path": minio_path, "hash": image_hash})

            # Создаем задачу только для первого фото в группе
            if not current_group["task_created"]:
                current_group["task_created"] = True
                asyncio.create_task(
                    process_media_group(
                        media_group_id, 
                        update, 
                        context, 
                        CatchTgTable, 
                        CatchTgImage, 
                        UserTgTable
                    )
                )

            
            return ConversationHandler.END

        else:
            # Обработка одиночного фото
            photo_file = await update.message.photo[-1].get_file()
            #photo_path = f"tg/{user.id}_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')}.jpg"
            #await photo_file.download_to_drive(photo_path)
            #image_hash = calculate_image_hash(photo_path)
            file_bytes = await photo_file.download_as_bytearray()
            object_name = f"tg/{user.id}_post_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')}.jpg"
            minio_path = await upload_to_minio(file_bytes, object_name)
            if minio_path:
                # Вычисляем хеш из байтов без сохранения на диск
                image_hash = calculate_image_hash(file_bytes)


            # Сохранение одиночного фото
            context.user_data.setdefault("images", [])
            context.user_data["images"].append({"path": minio_path, "hash": image_hash})

            await update.message.reply_text("Фото успешно добавлено!")
    else:
        # Пользователь не отправил фото
        await update.message.reply_text(
            "Вы не отправили фото. Попробуйте еще раз, это нужно для подтверждения улова.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CREATE_POST_IMAGE


    userid = get_user_id_by_userid(user.id)
    # Сохраняем данные поста в базу данных
    stmt = CatchTgTable.insert().values(
        user_id=userid,
        about=context.user_data.get('about'),
        weight=context.user_data.get('weight'),
        bait=context.user_data.get('bait'),
        location_name=context.user_data.get('location_name'),
        fish=context.user_data.get('fish'),

    )

    try:
        with engine.connect() as conn:
            result = conn.execute(stmt)
            conn.commit()

            new_post_id = result.inserted_primary_key[0]
            context.user_data["id"] = new_post_id

            # Сохраняем изображения одиночного поста
            for photo in context.user_data.get("images", []):
                stmt_img = CatchTgImage.insert().values(
                    cacthtg_id=new_post_id,
                    image=photo["path"],
                    image_hash=photo["hash"]
                )
                conn.execute(stmt_img)
            conn.commit()
        print(context.user_data.get("id"))
        await send_post_to_channel(update, context, CatchTgTable, UserTgTable, CatchTgImage)

        if result.rowcount > 0:
            logger.info(f"Пользователь {user.id} успешно создал пост.")
        else:
            logger.warning(f"Пользователь {user.id} не смог создать пост.")
            await update.message.reply_text("Произошла ошибка при сохранении поста. Попробуйте снова.")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при сохранении поста пользователя {user.id}: {e}")
        await update.message.reply_text("Произошла ошибка при сохранении поста. Попробуйте снова.")
        return ConversationHandler.END

    # Отправляем пост в канал

    context.user_data.pop("images", None)
    
    return ConversationHandler.END


async def send_post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, CatchTgTable, UserTgTable, CatchTgImage):
    """Отправка поста в Telegram-канал."""
    user = update.effective_user

    # Получаем данные пользователя из базы данных
    user_query = UserTgTable.select().where(UserTgTable.c.userid == user.id)
    with engine.connect() as conn:
        user_result = conn.execute(user_query).fetchone()

    if not user_result:
        logger.warning(f"Пользователь {user.id} не найден при отправке поста в канал.")
        await update.message.reply_text("Ошибка: Профиль не найден. Пост не может быть отправлен.")
        return

    # Получаем данные поста из context.user_data
    post_data = {
        'about': context.user_data.get('about'),
        'weight': context.user_data.get('weight'),
        'bait': context.user_data.get('bait'),
        'location_name': context.user_data.get('location_name'),
        'fish': context.user_data.get('fish'),
        'id': context.user_data.get('id'),
    }

    if not post_data['id']:  # Проверяем, есть ли ID
        logger.warning(f"Не найден id для поста пользователя {user.id}.")
        await update.message.reply_text("Ошибка: Не найден id. Попробуйте снова.")
        return

    # Формируем текст поста
    post_text = (
        f"<b>Новый Улов от {user_result.first_name} {user_result.last_name}</b>\n\n"
        f"Рыба: {post_data['fish']}\n"
        f"Вес: {post_data['weight']} грамм\n"
        f"Приманка: {post_data['bait']}\n"
        f"Локация: {post_data['location_name']}\n"
        f"Описание: {post_data['about'] or 'Не указано'}\n"
        f"Дата: {update.message.date.strftime('%Y-%m-%d')}"
    )

    # Отправляем пост в канал
    channel_id = CHANNEL_ID  # Замените на ID вашего канала
    message = None  # Переменная для хранения результата отправки
    media = []

    query_images = CatchTgImage.select().where(CatchTgImage.c.cacthtg_id == post_data['id'])
    with engine.connect() as conn:
        images_rows = conn.execute(query_images).fetchall()


    if images_rows and len(images_rows) > 0:
        # Формируем список объектов InputMediaPhoto
        for idx, row in enumerate(images_rows):

            try:
                # Скачиваем файл из MinIO в память
                response = minio_client.get_object(BUCKET_NAME, row.image)
                image_data = io.BytesIO(response.data)
                image_data.seek(0)
                
                # Создаем медиа-объект
                if idx == 0:
                    media.append(InputMediaPhoto(media=image_data, caption=post_text, parse_mode="HTML"))
                else:
                    media.append(InputMediaPhoto(media=image_data))
                    
            except S3Error as e:
                logger.error(f"Ошибка получения файла из MinIO: {e}")
                continue
            finally:
                response.close()
                response.release_conn()


            # photo_path = row.image  # предполагается, что в этом поле хранится путь к файлу
            # if os.path.exists(photo_path):
            #     file_obj = open(photo_path, 'rb')
            #     if idx == 0:
            #         # Первому фото добавляем подпись (caption)
            #         media.append(InputMediaPhoto(media=file_obj, caption=post_text, parse_mode="HTML"))
            #     else:
            #         media.append(InputMediaPhoto(media=file_obj))
            # else:
            #     logger.warning(f"Фото поста не найдено: {photo_path}")
        try:
            messages = await context.bot.send_media_group(chat_id=channel_id, media=media)
            message_id = messages[0].message_id if messages else None

                        # Закрываем все BytesIO объекты

        except Exception as e:
            logger.error(f"Ошибка при отправке медиа-группы: {e}")
            sent_message = await context.bot.send_message(chat_id=channel_id, text=post_text, parse_mode="HTML")
            message_id = sent_message.message_id
        finally:
            # Закрываем все открытые файловые дескрипторы
            for item in media:
                try:
                    if hasattr(item.media, 'close'):
                        item.media.close()
                except Exception as e:
                    logger.error(f"Ошибка при закрытии файла: {e}")
    else:
        # Если изображений нет, отправляем текстовое сообщение
        sent_message = await context.bot.send_message(chat_id=channel_id, text=post_text, parse_mode="HTML")
        message_id = sent_message.message_id



    # Обновляем запись поста, записывая message_id
    if message_id:
        update_query = (
            CatchTgTable.update()
            .where(CatchTgTable.c.id == post_data['id'])
            .values(message_id=message_id)
        )
        with engine.connect() as conn:
            conn.execute(update_query)
            conn.commit()


    logger.info(f"Пост пользователя {user.id} успешно отправлен в канал.")
    await update.message.reply_text("Ваш пост успешно отправлен в канал!", reply_markup=get_main_keyboard(True))


async def cancel_create_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена создания поста."""
    user = update.effective_user

    if update.message:
        # Отмена через текстовое сообщение
        logger.info(f"Пользователь {user.id} отменил создание поста через текст 'Отмена'.")
        await update.message.reply_text("Создание поста отменено.", reply_markup=get_main_keyboard(True))
    elif update.callback_query:
        # Отмена через Inline-кнопку
        query = update.callback_query
        await query.answer()  # Подтверждаем нажатие кнопки
        logger.info(f"Пользователь {user.id} отменил создание поста через Inline-кнопку.")
        await query.message.reply_text("Создание поста отменено.", reply_markup=get_main_keyboard(True))
    else:
        logger.warning(f"Неизвестный тип обновления при отмене создания поста для пользователя {user.id}.")
        return ConversationHandler.END

    # Очищаем временные данные из context.user_data
    context.user_data.pop('about', None)
    context.user_data.pop('weight', None)
    context.user_data.pop('bait', None)
    context.user_data.pop('location_name', None)
    context.user_data.pop('fish', None)
    context.user_data.pop('image', None)

    return ConversationHandler.END

# Диалог создания поста
create_post_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_post_button, pattern=f"^{CALLBACK_CREATE_POST}$")],
    states={
        CREATE_POST_ABOUT: [
                            MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_about),  
                            CallbackQueryHandler(cancel_create_post, pattern=f"^{CALLBACK_CANCEL_POST}$")
                            ],
        CREATE_POST_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_weight),
                             CallbackQueryHandler(cancel_create_post, pattern=f"^{CALLBACK_CANCEL_POST}$")],
        CREATE_POST_BAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_bait)],
        CREATE_POST_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_location)],
        CREATE_POST_FISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_post_fish)],
        CREATE_POST_IMAGE: [
            MessageHandler(filters.PHOTO, lambda u, c: create_post_image(u, c, CatchTgTable, UserTgTable, CatchTgImage)),
            MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: create_post_image(u, c, CatchTgTable, UserTgTable, CatchTgImage))
        ],
    },
    fallbacks=[
        MessageHandler(filters.Regex('^Отмена$'), cancel_create_post),  # Отмена через текст "Отмена"
        CallbackQueryHandler(cancel_create_post, pattern=f"^{CALLBACK_CANCEL_POST}$")  # Отмена через Inline-кнопку
    ]
)