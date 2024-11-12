from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('bitcoin_assets.urls')),
    path('admin/', admin.site.urls),
]
