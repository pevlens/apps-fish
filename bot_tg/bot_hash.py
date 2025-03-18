from PIL import Image
import imagehash
import io

def calculate_image_hash(image_bytes: bytes) -> str | None:
    """Вычисляет хэш изображения и возвращает в виде шестнадцатеричной строки"""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        hash_obj = imagehash.average_hash(image)
        return str(hash_obj)  # Конвертируем в строковое представление
    except Exception as e:
        print(f"Ошибка при вычислении хэша: {e}")
        return None

