import os
import sys

# Проверка, запущено ли приложение как скомпилированный exe-файл
if getattr(sys, 'frozen', False):
    # Если это exe, берем путь из временной папки PyInstaller
    BASE_DIR = sys._MEIPASS
else:
    # Если это обычный скрипт, берем путь на уровень выше
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# путь к файлу базы данных
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), "film_catalog.db")
else:
    DB_PATH = os.path.join(BASE_DIR, "film_catalog.db")

# папка с ресурсами (постеры)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# стандартный постер
DEFAULT_POSTER = os.path.join(ASSETS_DIR, "sample_poster.png")

# список жанров
DEFAULT_GENRES = [
    "Боевик", "Комедия", "Драма", "Фантастика",
    "Ужасы", "Триллер", "Мультфильм", "Документальный",
]

# корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# путь к файлу базы данных
DB_PATH = os.path.join(BASE_DIR, "film_catalog.db")

# папка с ресурсами
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# стандартный постер, если у фильма нет своего
DEFAULT_POSTER = os.path.join(ASSETS_DIR, "sample_poster.png")

# стандартный аудиофайл
SAMPLE_AUDIO = os.path.join(ASSETS_DIR, "sample_audio.wav")

# список жанров
DEFAULT_GENRES = [
    "Боевик", "Комедия", "Драма", "Фантастика",
    "Ужасы", "Триллер", "Мультфильм", "Документальный",
]