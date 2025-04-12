# Bilibili 下载器 (Django版)

这是一个基于Django框架的Bilibili视频下载工具，支持通过URL或BV号下载视频和音频内容。

## 功能特点

- 支持通过URL或BV号下载Bilibili视频
- 支持下载视频或仅下载音频
- 支持将音频转换为MP3格式
- 提供已下载文件的列表和管理
- 美观的用户界面

## 安装说明

1. 克隆或下载本项目
2. 安装依赖包：
   ```
   pip install -r requirements.txt
   ```
3. 运行Django开发服务器：
   ```
   python manage.py runserver
   ```
4. 在浏览器中访问 http://127.0.0.1:8000/

## 使用方法

1. 在首页输入Bilibili视频的URL或BV号
2. 选择下载类型（视频或音频）
3. 如果选择音频，可以勾选是否转换为MP3格式
4. 点击下载按钮开始下载
5. 下载完成后，可以在文件列表中查看和下载文件

## 技术栈

- Django: Web框架
- yt-dlp: 视频下载库
- JavaScript: 前端交互
- CSS: 样式和布局

## 注意事项

- 本工具仅供学习和个人使用
- 请尊重版权，不要下载和分享受版权保护的内容
- 在生产环境中使用前，请确保更改Django的SECRET_KEY并关闭DEBUG模式