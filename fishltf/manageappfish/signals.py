import requests
import logging
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import CacthTg
import os

logger = logging.getLogger(__name__)



@receiver(post_delete, sender=CacthTg)
def send_deletion_request(sender, instance, **kwargs):
    """
    При удалении записи из CacthTg отправляем POST-запрос на API-сервер.
    """
    API_URL = os.getenv('API_URL', 'api')
    API_PORT  = os.getenv('API_PORT', '5000')
    API_KEY =  os.getenv('X-API-KEY', 'qwdqwd')
    API_SCHEME =  os.getenv('API_SCHEME', 'http')
    API_PATH =  os.getenv('API_PATH', '/send_message')

    payload = {
    'user_id': instance.user.userid,  # замените на нужный user_id
    'message': 'Привет, Ваш улов не был потвержден Администратором так как были ранее дубликаты такого фото.',
    'html': True,          # укажите True, если сообщение содержит HTML-разметку
    "channel_message_id": instance.message_id,
    # Если нужно удалить сообщение из канала, раскомментируйте и задайте параметры:
    # 'channel_id': -1001234567890,  # ID канала
    # 'channel_message_id': 42       # ID сообщения, которое нужно удалить
    }

    # payload = {
    #     "id": instance.pk,
    #     "user_id": instance.user.userid,
    #     "deleted_at": instance.created_at.isoformat(),
    #     "about": instance.about,
    #     "fish": instance.fish,
    # }
    api_url = f"{API_SCHEME}://{API_URL}:{API_PORT}{API_PATH}"  # замените на реальный URL вашего API
    headers = {
    'X-API-Key': API_KEY, # замените на ваш действующий API ключ
    'Content-Type': 'application/json'
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers,timeout=10)
        response.raise_for_status()
        logger.info(f"Запрос на удаление успешно отправлен для записи {instance.pk}")
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса на удаление для записи {instance.pk}: {e}")




