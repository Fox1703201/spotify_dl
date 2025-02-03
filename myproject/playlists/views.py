import os
import subprocess
import shutil
import zipfile
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings

# Папка для временного хранения скачанных файлов
DOWNLOAD_PATH = os.path.join(settings.BASE_DIR, "temp_downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

@csrf_exempt
def index(request):
    """Отображает HTML-страницу и обрабатывает скачивание."""
    
    if request.method == "POST":
        playlist_url = request.POST.get("playlist_url")
        if not playlist_url:
            return JsonResponse({"error": "Вы не указали ссылку на плейлист"}, status=400)

        # Создаём уникальную папку для скачивания
        session_folder = os.path.join(DOWNLOAD_PATH, f"session_{os.getpid()}")
        os.makedirs(session_folder, exist_ok=True)

        try:
            # Запускаем spotdl для скачивания
            command = [
                    "spotdl", "download", playlist_url, 
                    "--output", os.path.join(session_folder, "{artist} - {title}.mp3")
                        ]

            subprocess.run(command, check=True)

            # Проверяем, скачались ли файлы
            files = [f for f in os.listdir(session_folder) if f.endswith(".mp3")]
            if not files:
                return JsonResponse({"error": "Ошибка: Треки не были скачаны"}, status=500)

            # Создаём ZIP-архив
            zip_filename = f"playlist_{os.getpid()}.zip"
            zip_filepath = os.path.join(DOWNLOAD_PATH, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    zipf.write(os.path.join(session_folder, file), file)

            # Удаляем временные файлы после скачивания
            shutil.rmtree(session_folder)

            # Отправляем ZIP пользователю
            return FileResponse(open(zip_filepath, "rb"), as_attachment=True, filename="playlist.zip")

        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": f"Ошибка при скачивании: {str(e)}"}, status=500)

    return render(request, "index.html")


