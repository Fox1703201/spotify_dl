from django.contrib import admin
from django.urls import path, include  # include - для подключения других маршрутов

urlpatterns = [
    path('admin/', admin.site.urls),  # Админка Django
    path('', include('playlists.urls')),  # Подключаем маршруты из playlists
]
