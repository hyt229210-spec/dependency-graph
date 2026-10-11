"""Получение изображения графа через PlantUML и показ его на экране."""
import os
import subprocess
import webbrowser
from pathlib import Path

RENDER_TIMEOUT_SECONDS = 90


class RenderError(Exception):
    """Ошибка получения изображения."""


def save_text(text, path):
    """Сохраняет текст в файл (создавая папку) и возвращает путь."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def render_png(puml_path, jar_path):
    """Превращает .puml в .png программой PlantUML, возвращает путь к картинке."""
    if not Path(jar_path).is_file():
        raise RenderError(f"Не найден файл PlantUML: {jar_path}")
    command = ["java", "-jar", str(jar_path), "-charset", "UTF-8", str(puml_path)]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=RENDER_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        raise RenderError("Java не найдена: проверьте команду 'java -version'")
    except subprocess.TimeoutExpired:
        raise RenderError("PlantUML не ответил за отведённое время")
    png_path = Path(puml_path).with_suffix(".png")
    if result.returncode != 0 or not png_path.is_file():
        details = (result.stderr or result.stdout).strip()
        raise RenderError(f"PlantUML завершился с ошибкой: {details}")
    return png_path


def show_image(png_path):
    """Открывает картинку на экране программой по умолчанию."""
    if hasattr(os, "startfile"):
        os.startfile(str(png_path))
    else:
        webbrowser.open(Path(png_path).resolve().as_uri())