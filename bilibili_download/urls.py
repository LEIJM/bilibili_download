from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bilibili_downloader.urls')),  # 将所有请求路由到我们的应用
]