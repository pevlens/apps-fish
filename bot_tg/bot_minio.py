from minio import Minio
from minio.error import S3Error
import os
import io
# Настройки подключения
minio_client = Minio(
    os.getenv('MINIO_STORAGE_ENDPOINT', 'admin'),  # Адрес MinIO-сервера
    access_key= os.getenv('AWS_ACCESS_KEY_ID', 'admin') ,  # Ключ доступа
    secret_key= os.getenv('AWS_SECRET_ACCESS_KEY', 'passwrd') ,  # Секретный ключ
    secure=True  # Использовать HTTPS (True/False)
)



BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'passwrd') 

# Проверяем и создаем бакет если нужно
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

async def upload_to_minio(file_bytes, object_name):
    try:
        file_stream = io.BytesIO(file_bytes)
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            file_stream,
            length=len(file_bytes),
            metadata={
                            "Content-Type": "image/jpeg",
                            "Content-Disposition": "inline",
                            "Cache-Control": "max-age=86400"
                        },
            content_type="image/jpeg"
        )
        return f"{object_name}"
    except S3Error as exc:
        print(f"Error uploading to MinIO: {exc}")
        return None
    

async def delete_from_minio(object_path: str) -> bool:
    """
    Удаляет файл из MinIO
    :param object_path: Полный путь к файлу в формате "bucket-name/object-path"
    :return: True если удаление успешно, False в случае ошибки
    """
    try:
        # Разбиваем путь на бакет и объект
        bucket_name, object_name = object_path.split('/', 1)
        
        minio_client.remove_object(bucket_name, object_name)
        return True
        
    except S3Error as exc:
        print(f"Error deleting from MinIO: {exc}")
        return False
    except ValueError as exc:
        print(f"Invalid object path format: {object_path}")
        return False