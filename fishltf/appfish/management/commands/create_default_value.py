from django.core.management.base import BaseCommand
from appfish.models import Gear, Method, Fish

class Command(BaseCommand):
    help = 'Добавление дефолтных значений в таблицы FISH, GEAR, Method'
    
    def handle(self, *args, **kwargs):
        # Добавление рыб с проверкой уникальности по имени
        fish_values = [
            {"name": "Карась серебряный", "threshold_small": 100, "threshold_medium": 300, "threshold_big": 800, "threshold_trophy": 1500,"point": 10},
            {"name": "Карась золотой", "threshold_small": 100, "threshold_medium": 300, "threshold_big": 800, "threshold_trophy": 1500,"point": 12},
            {"name": "Линь", "threshold_small": 200, "threshold_medium": 800, "threshold_big": 2000, "threshold_trophy": 4000,"point": 11},
            {"name": "Лещ", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 3000, "threshold_trophy": 5000,"point": 12},
            {"name": "Плотва", "threshold_small": 100, "threshold_medium": 500, "threshold_big": 1000, "threshold_trophy": 2000,"point": 11},
            {"name": "Красноперка", "threshold_small": 100, "threshold_medium": 500, "threshold_big": 1000, "threshold_trophy": 2000,"point": 10},
            {"name": "Густера", "threshold_small": 100, "threshold_medium": 500, "threshold_big": 1000, "threshold_trophy": 2000,"point": 12},
            {"name": "Сазан", "threshold_small": 300, "threshold_medium": 4000, "threshold_big": 8000, "threshold_trophy": 15000,"point": 14},
            {"name": "Карп обыкновенный", "threshold_small": 300, "threshold_medium": 4000, "threshold_big": 8000, "threshold_trophy": 15000,"point": 13},
            {"name": "Карп Зеркальный", "threshold_small": 300, "threshold_medium": 4000, "threshold_big": 8000, "threshold_trophy": 15000,"point": 14},
            {"name": "Толстолобик", "threshold_small": 2000, "threshold_medium": 5000, "threshold_big": 10000, "threshold_trophy": 20000,"point": 14},
            {"name": "Амур черный", "threshold_small": 1000, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 15},
            {"name": "Амур белый", "threshold_small": 250, "threshold_medium": 600, "threshold_big": 1200, "threshold_trophy": 2000,"point": 14},

            {"name": "Язь", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 3000, "threshold_trophy": 5000,"point": 14},
            {"name": "Пескарь", "threshold_small": 10, "threshold_medium": 50, "threshold_big": 100, "threshold_trophy": 200,"point": 10},
            {"name": "Вьюн", "threshold_small": 50, "threshold_medium": 150, "threshold_big": 300, "threshold_trophy": 500,"point": 11},
            {"name": "Ёрш", "threshold_small": 50, "threshold_medium": 150, "threshold_big": 300, "threshold_trophy": 500,"point": 11},
            {"name": "Уклейка", "threshold_small": 10, "threshold_medium": 50, "threshold_big": 100, "threshold_trophy": 200,"point": 10},

            {"name": "Окунь", "threshold_small": 100, "threshold_medium": 300, "threshold_big": 800, "threshold_trophy": 1500,"point": 12},
            {"name": "Щука", "threshold_small": 800, "threshold_medium": 3500, "threshold_big": 6000, "threshold_trophy": 12000,"point": 15},
            {"name": "Судак", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 17},
            {"name": "Сом обыкновенный", "threshold_small": 3000, "threshold_medium": 10000, "threshold_big": 40000, "threshold_trophy": 80000,"point": 20},
            {"name": "Сом канадский", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 2000, "threshold_trophy": 3000,"point": 20},
            {"name": "Жерех", "threshold_small": 1000, "threshold_medium": 3000, "threshold_big": 6000, "threshold_trophy": 10000,"point": 18},
            {"name": "Голавль", "threshold_small": 500, "threshold_medium": 1500, "threshold_big": 4000, "threshold_trophy": 7000,"point": 18},
            
            {"name": "Елец", "threshold_small": 100, "threshold_medium": 500, "threshold_big": 1000, "threshold_trophy": 2000,"point": 18},
        
            {"name": "Стерлядь", "threshold_small": 500, "threshold_medium": 1500, "threshold_big": 4000, "threshold_trophy": 8000,"point": 21},
            {"name": "Форель", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 3000, "threshold_trophy": 6000,"point": 20},
            {"name": "Хариус", "threshold_small": 200, "threshold_medium": 800, "threshold_big": 2000, "threshold_trophy": 4000,"point": 20},
            {"name": "Налим", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 20},
            
            {"name": "Буффало", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 20},

            {"name": "Ротан", "threshold_small": 50, "threshold_medium": 200, "threshold_big": 500, "threshold_trophy": 1000,"point": 13},
            {"name": "Чехонь", "threshold_small": 100, "threshold_medium": 500, "threshold_big": 1000, "threshold_trophy": 2000,"point": 14},
            {"name": "Берш", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 14},
            {"name": "Подуст", "threshold_small": 200, "threshold_medium": 600, "threshold_big": 1200, "threshold_trophy": 2500,"point": 15},
            {"name": "Синец", "threshold_small": 150, "threshold_medium": 700, "threshold_big": 1500, "threshold_trophy": 3000,"point": 15},
            {"name": "Терпуг", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 3000, "threshold_trophy": 6000,"point": 15},
            {"name": "Минога", "threshold_small": 100, "threshold_medium": 300, "threshold_big": 800, "threshold_trophy": 1500,"point": 15},
            {"name": "Муксун", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 15},
            {"name": "Нельма", "threshold_small": 1000, "threshold_medium": 3000, "threshold_big": 6000, "threshold_trophy": 10000,"point": 20},
            {"name": "Омуль", "threshold_small": 500, "threshold_medium": 1500, "threshold_big": 4000, "threshold_trophy": 8000,"point": 17},
            {"name": "Пелядь", "threshold_small": 300, "threshold_medium": 1000, "threshold_big": 3000, "threshold_trophy": 6000,"point": 17},
            {"name": "Ряпушка", "threshold_small": 100, "threshold_medium": 400, "threshold_big": 1000, "threshold_trophy": 2000,"point": 14},
            {"name": "Сиг", "threshold_small": 500, "threshold_medium": 2000, "threshold_big": 5000, "threshold_trophy": 10000,"point": 18}
        ]

        for data in fish_values:
            obj, created = Fish.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Рыба "{data["name"]}" создана'))
            else:
                self.stdout.write(f'Рыба "{data["name"]}" уже существует')

        # Добавление методов ловли
        methods_list = [
            "поплавочный",
            "фидерный",
            "твитчинг",
            "искусственные приманки",
            "Нахлыст",
            "Донка",
            "Тролинг",
            "Кастинг",
            "Зимняя",
            "Живец",
            "Подводная охота",
        ]

        for method in methods_list:
            obj, created = Method.objects.get_or_create(name=method)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Метод "{method}" создан'))
            else:
                self.stdout.write(f'Метод "{method}" уже существует')

        # Добавление снаряжения
        gear_list = [ 
            "Балонское Удилище", 
            "Маховое Удилище",
            "Матчевое Удилище",
            "Фидерное Удилище",
            "Спининговое Удилище",
            "Кастинговое Удилище",
            "Нахлыстовое Удилище",
            "Зимнее Удилище",
            "кружок-жерлица",
            "Ружьё",
        ]

        for gear in gear_list:
            obj, created = Gear.objects.get_or_create(name=gear)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Снаряжение "{gear}" создано'))
            else:
                self.stdout.write(f'Снаряжение "{gear}" уже существует')