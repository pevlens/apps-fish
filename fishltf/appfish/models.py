from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.text import slugify
from manageappfish.models import CacthTgImage
import os
# Create your models here.



class Gear (models.Model):

    name =  models.CharField(max_length=50,blank=True,null=True)
    description = models.TextField()


    def __str__(self):
        return self.name

class Method (models.Model):

    name = models.CharField(max_length=50,blank=True,null=True)
    description = models.TextField()

    
    def __str__(self):
        return self.name


class Place(models.Model):
    #catch = models.ForeignKey(Catch,  related_name='catch', on_delete=models.SET_NULL,blank=True,null=True)
    location_name = models.CharField(max_length=100)
    location_geo = models.CharField(max_length=100,  blank=True, null=True)
    about = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.location_name
    
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gear_main =  models.ForeignKey(Gear, related_name='gear', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Основкая снасть")
    metod_catch = models.ForeignKey(Method, on_delete=models.SET_NULL, blank=True, null=True ,related_name='metod', verbose_name="основной метод ловли")
    bio = models.TextField("Биография", blank=True, null=True)
    alias = models.TextField("Псевдоним", blank=True, null=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField("Дата рождения", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    slug = models.SlugField("URL Slug", unique=True, blank=True)

    def get_age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None  # Если нет даты рождения

    def save(self, *args, **kwargs):
        # Если slug не задан, генерируем его автоматически
        if not self.slug:
            # Используем alias, если он указан, иначе используем имя пользователя
            base_slug = slugify(self.alias) if self.alias else slugify(self.user.username)
            slug_candidate = base_slug
            num = 1
            # Проверяем на уникальность slug
            while Profile.objects.filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{num}"
                num += 1
            self.slug = slug_candidate
        

        if self.avatar:
            filename = os.path.basename(self.avatar.name)
            self.avatar.name = os.path.join('avatars', filename)


        super().save(*args, **kwargs)

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'
    
class Fish(models.Model):
    name = models.CharField("Название", max_length=150 ,unique=True, blank=False, null=False )
    baitfish = models.FloatField("Порог для живца", help_text="Вес в гр.ниже этого значения - живец", default=1)
    threshold_small = models.FloatField("Порог для маленькой рыбы", help_text="Вес в гр.ниже этого значения - маленькая")
    threshold_medium = models.FloatField("Порог для средней рыбы", help_text="Вес в гр. ниже этого значения - средняя")
    threshold_big = models.FloatField("Порог для большой рыбы", help_text="Вес в гр. ниже этого значения - большая")
    threshold_trophy = models.FloatField("Порог для трофейной рыбы", help_text="Вес в гр. ниже этого значения - трофейная")
    point = models.IntegerField (blank=False, null=False, default=0)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Вид рыбы"
        verbose_name_plural = "Виды рыб"

    def __str__(self):
        return self.name
    

class Catch(models.Model):
    user =  models.ForeignKey(User, related_name='fishman_catch', on_delete=models.CASCADE)
    fish_species = models.ForeignKey(Fish, on_delete=models.CASCADE, related_name='fish_catch', verbose_name="Вид рыбы")
    location_name = models.ForeignKey(Place, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ForeignKey(CacthTgImage, on_delete=models.CASCADE, related_name='fish_image_catch', verbose_name="Основное фото", blank=True, null=True)
    bait = models.TextField(blank=True,null=True)
    weight = models.IntegerField(blank=False,null=False)
    length = models.IntegerField(blank=True,null=True)
    size = models.CharField("Размер", max_length=20, blank=True)
    about = models.TextField(blank=True,null=True)
#    image = models.ImageField(upload_to='catch/', blank=True, null=True)
    date_catch  = models.DateField()
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
#    image_hash = models.CharField(max_length=164, db_index=True, blank=True, null=True)

    def calculate_points(self):
        if self.fish_species.point is None:
            return 0  # Если point не задан, возвращаем 0
        size = self.size
        size_multiplier = {
            "baitfish": 0.1,
            "small": 1,
            "medium": 4,
            "big": 7,
            "trophy": 12,
            "record": 13,
        }
        return self.fish_species.point * size_multiplier.get(size, 1)


    def save(self, *args, **kwargs): 

        if self.weight is None:
            raise ValueError("Поле 'weight' не может быть None")

        if self.fish_species is None:
            raise ValueError("Поле 'fish_species' не может быть None")



        if self.weight <= self.fish_species.baitfish:
            self.size = "baitfish"

        elif self.fish_species.baitfish < self.weight <= self.fish_species.threshold_small:
            self.size = "small"
        
        elif self.fish_species.threshold_small < self.weight <= self.fish_species.threshold_medium:
            self.size = "medium"
        
        elif self.fish_species.threshold_medium < self.weight <= self.fish_species.threshold_big:
            self.size = "big"
        
        elif self.fish_species.threshold_big < self.weight <= self.fish_species.threshold_trophy:
            self.size = "trophy"
        else: 
            self.size = "record"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()}-{self.fish_species.name}-{self.date_catch}"

    pass




