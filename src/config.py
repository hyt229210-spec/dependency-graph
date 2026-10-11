"""Чтение и проверка конфигурационного файла (JSON)."""
import json
import os

MIN_DEPTH = 1
REQUIRED_KEYS = [
    "package_name",
    "repository",
    "test_mode",
    "ascii_tree",
    "max_depth",
    "filter_substring",
]


class ConfigError(Exception):
    """Ошибка в конфигурационном файле."""


def load_config(path):
    """Читает JSON-файл и возвращает проверенный словарь параметров."""
    try:
        with open(path, encoding="utf-8") as config_file:
            data = json.load(config_file)
    except FileNotFoundError:
        raise ConfigError(f"Файл конфигурации не найден: {path}")
    except OSError as error:
        raise ConfigError(f"Не удалось прочитать файл конфигурации: {error}")
    except json.JSONDecodeError as error:
        raise ConfigError(f"Файл не является корректным JSON: {error}")
    if not isinstance(data, dict):
        raise ConfigError("Корнем JSON-файла должен быть объект {...}")
    return validate_config(data)


def validate_config(data):
    """Проверяет все параметры и возвращает только нужные."""
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ConfigError("Не заданы параметры: " + ", ".join(missing))
    _check_text(data, "package_name", allow_empty=False)
    _check_text(data, "repository", allow_empty=False)
    _check_text(data, "filter_substring", allow_empty=True)
    _check_bool(data, "test_mode")
    _check_bool(data, "ascii_tree")
    _check_depth(data["max_depth"])
    _check_repository(data["repository"], data["test_mode"])
    return {key: data[key] for key in REQUIRED_KEYS}


def _check_text(data, key, allow_empty):
    """Параметр должен быть строкой (пустой - только если разрешено)."""
    value = data[key]
    if not isinstance(value, str):
        raise ConfigError(f"Параметр '{key}' должен быть строкой")
    if not allow_empty and not value.strip():
        raise ConfigError(f"Параметр '{key}' не должен быть пустым")


def _check_bool(data, key):
    """Параметр должен быть true или false."""
    if not isinstance(data[key], bool):
        raise ConfigError(f"Параметр '{key}' должен быть true или false")


def _check_depth(value):
    """Глубина анализа - целое число не меньше минимальной."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError("Параметр 'max_depth' должен быть целым числом")
    if value < MIN_DEPTH:
        raise ConfigError(
            f"Параметр 'max_depth' должен быть не меньше {MIN_DEPTH}"
        )


def _check_repository(value, test_mode):
    """В тестовом режиме нужен путь к файлу, иначе - URL."""
    if test_mode:
        if not os.path.isfile(value):
            raise ConfigError(f"Файл тестового репозитория не найден: {value}")
    elif not value.startswith(("http://", "https://")):
        raise ConfigError(
            "Параметр 'repository' должен быть URL (http:// или https://)"
        )