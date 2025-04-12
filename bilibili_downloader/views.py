import os
import re
import datetime
import yt_dlp
from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from urllib.parse import quote, unquote
import json


def download_content(url, save_path, content_type="video", cookies_file=None, enable_mp3_conversion=False):
    """
    下载视频或音频内容
    参数:
        url: 要下载的视频URL
        save_path: 保存文件的路径
        content_type: 'video'或'audio'
        cookies_file: cookies文件路径
        enable_mp3_conversion: 是否将音频转换为MP3格式
    """
    # 确保保存目录存在
    os.makedirs(save_path, exist_ok=True)

    # yt-dlp 基本下载配置
    ydl_opts = {
        'outtmpl': f"{save_path}/%(title)s.%(ext)s",  # 输出文件名模板
        'cookiefile': cookies_file if cookies_file and os.path.exists(cookies_file) else None,
    }

    # 根据内容类型设置不同的下载选项
    if content_type == "video":
        ydl_opts['format'] = 'bestvideo+bestaudio/best'  # 下载最佳视频和音频格式
        ydl_opts['merge_output_format'] = 'mp4'  # 合并输出格式为mp4
    elif content_type == "audio":
        ydl_opts['format'] = 'bestaudio/best'  # 下载最佳音频

        # 如果启用MP3转换
        if enable_mp3_conversion:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',  # 提取音频的插件
                'preferredcodec': 'mp3',  # 强制使用 MP3 编码
                'preferredquality': '192',  # 音质
            }]

    try:
        # 创建yt-dlp实例并下载内容
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '未知标题')
            ydl.download([url])
        return {"status": "success", "message": "下载完成!", "title": title}
    except Exception as e:
        return {"status": "error", "message": f"下载失败: {str(e)}"}


def is_url(text):
    """检查文本是否是URL"""
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// 或 https:// (可选)
        r'([a-zA-Z0-9-]+\.)*'  # 子域名 (可选)
        r'[a-zA-Z0-9-]+'  # 域名
        r'\.[a-zA-Z0-9-.]+'  # TLD
        r'(/.*)?$'  # 路径 (可选)
    )
    return bool(url_pattern.match(text))


def is_bvid(text):
    """检查文本是否是B站BV号"""
    bvid_pattern = re.compile(r'^BV[a-zA-Z0-9]{10}$')
    return bool(bvid_pattern.match(text))


def index(request):
    """首页路由，渲染 index.html 模板"""
    return render(request, 'index.html')


def help_view(request):
    """帮助路由，当访问根URL时显示服务状态信息"""
    return JsonResponse({
        "status": "online",
        "message": "文件下载服务已开启",
        "usage": "使用 /download/文件名 路径下载文件",
        "files": "使用 /files 查看可下载的文件列表"
    })


def format_file_size(size_bytes):
    """将字节大小格式化为人类可读的格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def list_files(request):
    """列出下载目录中的所有文件"""
    try:
        files = []
        for filename in os.listdir(settings.DOWNLOAD_FOLDER):
            file_path = os.path.join(settings.DOWNLOAD_FOLDER, filename)
            # 只列出文件，不列出子目录
            if os.path.isfile(file_path):
                # 获取文件大小
                file_size = os.path.getsize(file_path)

                # 获取文件创建时间和修改时间
                created_timestamp = os.path.getctime(file_path)
                modified_timestamp = os.path.getmtime(file_path)

                # 转换时间戳为可读日期格式
                created_date = datetime.datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                modified_date = datetime.datetime.fromtimestamp(modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')

                # 对文件名进行 URL 编码
                encoded_filename = quote(filename)

                file_info = {
                    "name": filename,
                    "size_bytes": file_size,
                    "size_formatted": format_file_size(file_size),
                    "created_date": created_date,
                    "modified_date": modified_date,
                    "download_url": f"/download/{encoded_filename}/"  # 使用编码后的文件名
                }
                files.append(file_info)

        # 按修改时间降序排序，最新的文件排在前面
        files.sort(key=lambda x: x["modified_date"], reverse=True)

        return JsonResponse({
            "message": "文件列表获取成功",
            "total_files": len(files),
            "files": files
        })
    except Exception as e:
        return JsonResponse({"error": f"获取文件列表失败: {str(e)}"}, status=500)


def download_file(request, filename):
    """下载指定文件"""
    # 安全检查，防止路径遍历攻击
    if '..' in filename or filename.startswith('/'):
        return JsonResponse({"error": "Invalid filename"}, status=400)

    # 对文件名进行 URL 解码
    decoded_filename = unquote(filename)

    file_path = os.path.join(settings.DOWNLOAD_FOLDER, decoded_filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{decoded_filename}"'
        return response

    return JsonResponse({"error": "File not found"}, status=404)


@csrf_exempt  # 禁用CSRF保护，因为这是API端点
@require_http_methods(["POST"])  # 只允许POST请求
def download_api(request):
    """处理下载请求的API"""
    try:
        # 解析JSON数据
        data = json.loads(request.body)

        if not data:
            return JsonResponse({"status": "error", "message": "请提供JSON数据"}, status=400)

        user_input = data.get('url', '').strip()
        content_type = data.get('type', 'video')  # 默认为视频
        enable_mp3 = data.get('mp3_conversion', False)  # 默认不转换为MP3

        if not user_input:
            return JsonResponse({"status": "error", "message": "URL或BV号不能为空!"}, status=400)

        # 自动判断输入类型
        if is_url(user_input):
            video_url = user_input
        elif is_bvid(user_input):
            video_url = f"https://www.bilibili.com/video/{user_input}"
        else:
            # 尝试将其视为BV号的部分，添加BV前缀
            if user_input.startswith("BV"):
                potential_bvid = user_input
            else:
                potential_bvid = "BV" + user_input

            if is_bvid(potential_bvid):
                video_url = f"https://www.bilibili.com/video/{potential_bvid}"
            else:
                # 假设它可能是一个不完整的URL
                if "bilibili.com" in user_input:
                    video_url = user_input
                else:
                    return JsonResponse({"status": "error", "message": "无法识别的输入格式!"}, status=400)

        # 设置下载路径
        download_path = settings.DOWNLOAD_FOLDER

        # cookies文件路径
        cookies_path = os.path.join(settings.BASE_DIR, 'bilibili.com_cookies.txt')

        # 执行下载
        result = download_content(video_url, download_path, content_type, cookies_path, enable_mp3)
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "无效的JSON数据"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"处理请求时出错: {str(e)}"}, status=500)