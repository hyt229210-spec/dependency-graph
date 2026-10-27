"""Получение прямых зависимостей пакета Rust (Cargo) из реестра пакетов.

Реестр (например, https://index.crates.io) хранит о каждом пакете один
текстовый файл: в каждой строке - JSON с описанием одной версии пакета,
включая список её зависимостей. Адрес реестра берётся из конфигурации.
"""
import http.client
import json
import re
import time
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 30
RETRY_COUNT = 3
RETRY_PAUSE_SECONDS = 2
HTTP_NOT_FOUND = 404
SHORT_NAME_MAX = 2
THREE_LETTER_NAME = 3
PREFIX_LENGTH = 2
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
NORMAL_KINDS = (None, "normal")


class CargoError(Exception):
    """Ошибка получения или разбора данных о пакете."""


class PackageNotFound(CargoError):
    """Пакета нет в реестре."""


def index_path(name):
    """Путь к файлу пакета в индексе реестра (правило, принятое в Cargo)."""
    lower = name.lower()
    if len(lower) <= SHORT_NAME_MAX:
        return f"{len(lower)}/{lower}"
    if len(lower) == THREE_LETTER_NAME:
        return f"{THREE_LETTER_NAME}/{lower[0]}/{lower}"
    first = lower[:PREFIX_LENGTH]
    second = lower[PREFIX_LENGTH:2 * PREFIX_LENGTH]
    return f"{first}/{second}/{lower}"


def package_url(registry, name):
    """Адрес файла с описанием пакета в реестре."""
    return f"{registry.rstrip('/')}/{index_path(name)}"


def download(url):
    """Одна попытка скачать файл. Если файла нет (404), возвращает None."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            return None
        raise CargoError(f"Ошибка загрузки ({error.code}): {url}")


def fetch_text(url):
    """Скачивает текстовый файл по ссылке. При сбое сети повторяет попытку."""
    last_error = None
    for attempt in range(RETRY_COUNT):
        if attempt:
            time.sleep(RETRY_PAUSE_SECONDS)
        try:
            return download(url)
        except (OSError, http.client.HTTPException) as error:
            last_error = error
    raise CargoError(
        f"Нет доступа к сети (попыток: {RETRY_COUNT}): {last_error}"
    )


def parse_entries(text):
    """Разбирает файл пакета: возвращает список описаний его версий."""
    entries = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise CargoError(f"Не удалось разобрать ответ реестра: {error}")
    return entries


def version_key(entry):
    """Ключ для сравнения версий: стабильные версии выше пробных."""
    core, dash, _ = entry["vers"].partition("+")[0].partition("-")
    numbers = tuple(
        int(part) if part.isdigit() else 0 for part in core.split(".")
    )
    return (not dash, numbers)


def latest_entry(entries):
    """Выбирает самую новую версию, не отозванную автором (yanked)."""
    available = [entry for entry in entries if not entry.get("yanked")]
    return max(available or entries, key=version_key)


def direct_dependencies(entry):
    """Имена обычных зависимостей версии.

    Пропускаются необязательные (optional), нужные только для разработки
    (dev) или сборки (build), а также привязанные к платформе (target).
    """
    names = []
    for dependency in entry.get("deps", []):
        if dependency.get("kind") not in NORMAL_KINDS:
            continue
        if dependency.get("optional") or dependency.get("target"):
            continue
        name = dependency.get("package") or dependency["name"]
        if name not in names:
            names.append(name)
    return names


def find_direct_dependencies(registry, package_name):
    """Возвращает прямые зависимости последней версии пакета из реестра."""
    if not NAME_PATTERN.match(package_name):
        raise CargoError(f"Недопустимое имя пакета: '{package_name}'")
    text = fetch_text(package_url(registry, package_name))
    entries = parse_entries(text) if text else []
    if not entries:
        raise PackageNotFound(f"Пакет '{package_name}' не найден в реестре")
    return direct_dependencies(latest_entry(entries))