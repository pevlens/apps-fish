# urls.py
from django.urls import path
from .views import HomePageView, ProfilePageView, TrophyPageView,StatsPageView, RulesPageView, AddUserPageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('profile/<slug:slug>/', ProfilePageView.as_view(), name='profile_detail'),
    path('trophy/', TrophyPageView.as_view(), name='trophy'),
    path('stats/', StatsPageView.as_view(), name='stats'),
    path('rules/', RulesPageView.as_view(), name='rules'),
    path('adduser/', AddUserPageView.as_view(), name='adduser'),
]
