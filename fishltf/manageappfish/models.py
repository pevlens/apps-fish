from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.text import slugify
# Create your models here.


class UserTg(models.Model):
    userid = models.BigIntegerField("id пользователя в телеграмм", unique=True, null=False)
    username = models.CharField("username в TG", max_length=100,blank=True,null=True)
    first_name =  models.CharField("имя в TG", max_length=100,blank=True,null=True)
    last_name =  models.CharField("фамилия в TG", max_length=100,blank=True,null=True)
    phone_number =  models.BigIntegerField("номер телефона в телеграмм", unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    metod_catch =  models.CharField("основной метод ловли", max_length=100,blank=True,null=True)
    gear_main =  models.CharField("оснавная снать", max_length=100,blank=True,null=True)
    bio =  models.CharField("об себе ", max_length=100,blank=True,null=True)
    alias =  models.CharField("Кличка", max_length=100,blank=True,null=True)
    birth_date  = models.DateField("Дата рождения",blank=True,null=True)
    profile_create = models.BooleanField("Создан ли профиль",default=False, blank=True,null=True)
    profile_change = models.BooleanField("Изменен ли профиль",default=False, blank=True,null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"{self.first_name}-{self.last_name}-{self.userid}-{self.username}"



class CacthTg(models.Model):
    user = models.ForeignKey(UserTg, related_name='fishman_tg', on_delete=models.CASCADE)
#    image = models.ImageField(upload_to='tg/', blank=True, null=True)
    about = models.TextField("Описание", blank=True,null=True)
    weight = models.IntegerField("Вес", blank=True,null=True)
    bait = models.TextField("приманка",blank=True,null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    location_name = models.CharField("Локация", blank=True, null=True,  max_length=200)
    fish =  models.CharField("Рыба", max_length=100,blank=True,null=True)
    post_add = models.BooleanField("Добавлен улов в основную базу",default=False, blank=True,null=True)
    message_id =  models.TextField("id сообщения пользователя в канале", null=False,default="0")
#    image_hash = models.CharField(max_length=164, db_index=True, blank=True, null=True)
    pass



class CacthTgImage(models.Model):
    cacthtg = models.ForeignKey(CacthTg, related_name='cacth_user_tg', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tg/', blank=True, null=True)
    image_hash = models.CharField(max_length=164, db_index=True, blank=True, null=True)

  

class TelegramMessage(models.Model):
    chat_id = models.BigIntegerField(blank=True,null=True)
    user_id = models.BigIntegerField(blank=True,null=True)
    message_text = models.TextField(blank=True,null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user_id}: {self.message_text}"