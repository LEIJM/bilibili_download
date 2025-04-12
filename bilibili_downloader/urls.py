from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 首页
    path('help/', views.help_view, name='help'),  # 帮助页面
    path('files/', views.list_files, name='list_files'),  # 文件列表
    path('download/<path:filename>/', views.download_file, name='download_file'),  # 下载文件
    path('downloads/', views.download_api, name='download_api'),  # 下载API
]