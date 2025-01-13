from django.urls import path

from .views import LoginPage


urlpatterns = [
    path('login/', LoginPage.as_view(), name='login'),
]
