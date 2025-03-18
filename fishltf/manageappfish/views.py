from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import UserTg
from appfish.models import  Profile, Catch,Fish,Place
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import  UserTg, CacthTg, CacthTgImage
from .forms import UserForm, ProfileForm, CatchForm
from django.db import IntegrityError
from django.core.files import File
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.forms import formset_factory
from django.db.models import Q



class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied()
        return super().handle_no_permission()


def permission_denied_view(request, exception):
    return render(request, '403.html', status=403)


class UnpublishedCatchesList(AdminRequiredMixin,ListView):
    model = CacthTg
    template_name = 'unpublished_list.html'
    context_object_name = 'catches'

    def get_queryset(self):
        return CacthTg.objects.filter(post_add=False)

class UserListView(AdminRequiredMixin, ListView):
    model = UserTg
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        """Фильтруем только тех пользователей, у которых profile_create = False"""
        return UserTg.objects.filter(profile_create = False)

class UserChangeListView(AdminRequiredMixin, ListView):
    model = UserTg
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        """Фильтруем только тех пользователей, у которых profile_create = False"""
        return UserTg.objects.filter(profile_change = True)


class CreateProfileView(AdminRequiredMixin, FormView):
    template_name = "profile_form.html"
    form_class = UserForm  # Основная форма (для контекста)
    success_url = reverse_lazy("user_list_registr")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tg = get_object_or_404(UserTg, pk=self.kwargs['pk'])
        
        # Инициализация начальных данных
        initial_user = {
            'first_name': user_tg.first_name,
            'last_name': user_tg.last_name,
        }
        
        initial_profile = {
            'alias': user_tg.alias,
            'birth_date': user_tg.birth_date,
        }

        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST, initial=initial_user)
            context['profile_form'] = ProfileForm(self.request.POST, self.request.FILES, initial=initial_profile)
        else:
            context['user_form'] = UserForm(initial=initial_user)
            context['profile_form'] = ProfileForm(initial=initial_profile)
        
        context['user_tg'] = user_tg
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        user_form = context['user_form']
        profile_form = context['profile_form']
        
        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        return self.form_invalid(user_form, profile_form)

    def form_valid(self, user_form, profile_form):
        user_tg = self.get_context_data()['user_tg']
        
        try:
            # Создаем или обновляем пользователя
            user, created = User.objects.update_or_create(
                username=f'tg_{user_tg.userid}',
                defaults={
                    'first_name': user_form.cleaned_data['first_name'],
                    'last_name': user_form.cleaned_data['last_name'],
                    'email': user_form.cleaned_data.get('email', ''),
                }
            )
            
            # Создаем или обновляем профиль
            profile, profile_created = Profile.objects.update_or_create(
                user=user,
                defaults={
                    'alias': profile_form.cleaned_data['alias'],
                    'birth_date': profile_form.cleaned_data['birth_date'],
                    'gear_main': profile_form.cleaned_data['gear_main'],
                    'metod_catch': profile_form.cleaned_data['metod_catch'],
                    'bio': profile_form.cleaned_data['bio'],
                }
            )
            
            # Обработка аватара
            if 'avatar' in profile_form.cleaned_data and profile_form.cleaned_data['avatar']:
                profile.avatar = profile_form.cleaned_data['avatar']
            elif not profile.avatar and user_tg.image:
                profile.avatar.save(
                    user_tg.image.name,
                    File(user_tg.image),
                    save=False
                )
            
            profile.save()
            
            # Обновляем статус в UserTg
            user_tg.profile_create = True
            user_tg.save()
            
        except IntegrityError as e:
            # Обработка ошибки уникальности
            print(f"Ошибка создания профиля: {str(e)}")
            #messages.error(self.request, f"Ошибка создания профиля: {str(e)}")
            return self.form_invalid(user_form, profile_form)
        
        return super().form_valid(user_form)

    def form_invalid(self, user_form, profile_form):
        return self.render_to_response(
            self.get_context_data(user_form=user_form, profile_form=profile_form)
        )




class CreateCacthView(AdminRequiredMixin, CreateView):
    template_name = 'create_catch.html'
    success_url = reverse_lazy('unpublished_catches')
 
    def get_extra(self):
        """
        Получаем количество дополнительных форм из GET-параметра 'extra'.
        Если параметр отсутствует или некорректен, по умолчанию extra = 1.
        """
        extra = self.request.GET.get('extra')
        try:
            extra = int(extra)
        except (TypeError, ValueError):
            extra = 1
        return extra

    def get_formset_class(self, extra):
        """
        Создаём класс Formset с динамическим числом форм.
        """
        return formset_factory(CatchForm, extra=extra, can_delete=True)

    def get(self, request, *args, **kwargs):
        # Получаем объект CacthTg по pk, переданному в URL
        catch_tg = get_object_or_404(CacthTg, pk=self.kwargs.get('pk'))
        extra = self.get_extra()
        FormsetClass = self.get_formset_class(extra)
        # Передаём catch_tg в каждую форму formset-а через form_kwargs
        formset = FormsetClass(form_kwargs={'catch_tg': catch_tg})

        try:
            user = User.objects.get(username=f"tg_{catch_tg.user.userid}")
        except User.DoesNotExist:
            user = None

         # Получаем все записи Catch этого пользователя, у которых есть изображение
        catch_photos = Catch.objects.filter(user=user, image__isnull=False)
        # Фильтруем по fish_filter, если параметр указан в GET-запросе
        fish_filter = self.request.GET.get('fish_filter', '')
        if fish_filter:
            catch_photos = catch_photos.filter(fish_species__name__icontains=fish_filter)

        hash_list = list(catch_tg.cacth_user_tg.values_list('image_hash', flat=True))
        duplicates = CacthTgImage.objects.filter(image_hash__in=hash_list).exclude(cacthtg=catch_tg)




        return render(request, self.template_name, {'formset': formset, 'catch_tg': catch_tg, 'catch_photos': catch_photos, 'hash_catch': duplicates})

    def post(self, request, *args, **kwargs):
        catch_tg = get_object_or_404(CacthTg, pk=self.kwargs.get('pk'))
        extra = self.get_extra()  # Используем то же значение extra для создания formset-а
        FormsetClass = self.get_formset_class(extra)
        formset = FormsetClass(request.POST, request.FILES, form_kwargs={'catch_tg': catch_tg})



                # Если в POST передана кнопка удаления, удаляем запись
        if "delete" in request.POST:
            catch_tg.delete()
            # При удалении сработает сигнал, если он настроен для отправки запроса к API
            return redirect(self.success_url)
        

        
        try:
            # Access the user correctly from the CatchTg instance
            user = User.objects.get(username=f"tg_{catch_tg.user.userid}")  # Ensure userid is the correct field
        except User.DoesNotExist:
            return render(request, self.template_name, {
                'formset': formset, 
                'catch_tg': catch_tg, 
                'error': f'User {catch_tg.user.userid} not found.'
            })

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    catch_instances = form.save(commit=False)  # Теперь это список!
                    for catch_instance in catch_instances:  # Проходим по списку объектов
                        catch_instance.user = user
                        # catch_instance.image = 
                        catch_instance.save()

      

            catch_tg.post_add = True
            catch_tg.save()

            return redirect(self.success_url)



        # Если форма не валидна, выводим ошибки
        print("Formset errors:", formset.errors)
        
        return render(request, self.template_name, {'formset': formset, 'catch_tg': catch_tg})




    pass