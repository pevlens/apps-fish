# urls.py
from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView


handler403 = permission_denied_view

urlpatterns = [
    path('auth/', LoginView.as_view(template_name='login.html', extra_context={'admin_login': True}), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),
    path('users-regist/', UserListView.as_view(), name='user_list_registr'),
    path('users-change/', UserChangeListView.as_view(), name='user_list_change'),
    path('profile/<int:pk>/', CreateProfileView.as_view(), name='create_profile'),
    path('unpublished-catches/', UnpublishedCatchesList.as_view(), name='unpublished_catches'),
    path('create-catch/<int:pk>/', CreateCacthView.as_view(), name='create-catch'),
]
