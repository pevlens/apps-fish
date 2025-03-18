# forms.py
from django import forms
from appfish.models import Profile, Gear, Method, Fish, Place, Catch
from .models import CacthTgImage
from django.contrib.auth.models import User
from django.forms import formset_factory
import copy
from django.utils.safestring import mark_safe

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['alias', 'birth_date', 'gear_main', 'metod_catch', 'avatar', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'gear_main': forms.Select(attrs={'class': 'form-select'}),
            'metod_catch': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }





class CatchForm(forms.ModelForm):
    count = forms.IntegerField(label="Количество", min_value=1, initial=1, widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 100px; text-align: center;',
        }))  # Новое поле
    class Meta:
        model = Catch
        # Здесь перечисляем поля, которые будут заполняться через форму.
        # Остальные поля (например, user) можно задавать в представлении.
        fields = ['fish_species', 'location_name', 'bait', 'weight', 'about', 'image', 'date_catch']

        widgets = {
            'fish_species': forms.Select(attrs={
                'class': 'form-control',
            }),
            'location_name': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название места',
            }),
            'bait': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите приманку',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Введите вес (кг)',
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание улова...',
            }),
            'image': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_catch': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем экземпляр CacthTg, если он передан
        self.catch_tg = kwargs.pop('catch_tg', None)
        super().__init__(*args, **kwargs)
        if self.catch_tg:
            # Устанавливаем начальные значения для полей из CacthTg
            self.fields['about'].initial = self.catch_tg.about
            self.fields['bait'].initial = self.catch_tg.bait
            # Устанавливаем только дату (без времени) из поля created_at модели CacthTg
            self.fields['date_catch'].initial = self.catch_tg.created_at.date()
            # Ограничиваем queryset поля image только изображениями, связанными с этой записью CacthTg
            self.fields['image'].queryset = CacthTgImage.objects.filter(cacthtg=self.catch_tg)


    def save(self, commit=True):
        # catch_instance = super().save(commit=False)
        # if commit:
        #     catch_instance.save()
        #     # Если был передан экземпляр CacthTg, обновляем его поле post_add
        #     if self.catch_tg:
        #         self.catch_tg.post_add = True
        #         self.catch_tg.save()
        # return catch_instance
        count = self.cleaned_data.get('count', 1)  # Получаем количество записей, которые нужно создать
        base_instance = super().save(commit=False)
        catch_instances = []
        for _ in range(count):
            # Создаем копию базового объекта
            new_instance = copy.copy(base_instance)
            # Обнуляем pk, чтобы Django создал новый объект при сохранении
            new_instance.pk = None
            if commit:
                new_instance.save()
            catch_instances.append(new_instance)
        # При необходимости можно также обработать m2m поля (new_instance.save_m2m())
        return catch_instances