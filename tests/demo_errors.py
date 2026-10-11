"""Демонстрация обработки ошибок для всех параметров конфигурации."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import ConfigError, validate_config

MISSING = object()

BASE = {
    "package_name": "serde",
    "repository": "https://github.com/serde-rs/serde",
    "test_mode": False,
    "ascii_tree": True,
    "max_depth": 3,
    "filter_substring": "test",
}

CASES = [
    ("Параметр не задан", "package_name", MISSING),
    ("Пустое имя пакета", "package_name", ""),
    ("Имя пакета не строка", "package_name", 123),
    ("Адрес не является URL", "repository", "not-a-url"),
    ("Тестовый режим, файла нет", "test_mode", True),
    ("Режим не true/false", "test_mode", "yes"),
    ("Вывод деревом не true/false", "ascii_tree", "да"),
    ("Глубина не число", "max_depth", "три"),
    ("Глубина меньше 1", "max_depth", 0),
    ("Подстрока не строка", "filter_substring", 5),
]


def build_config(key, value):
    """Копия правильной конфигурации с одним испорченным параметром."""
    data = dict(BASE)
    if value is MISSING:
        del data[key]
    else:
        data[key] = value
    return data


def main():
    """Проверяет каждый случай и печатает сообщение об ошибке."""
    for title, key, value in CASES:
        print(f"[{key}] {title}")
        try:
            validate_config(build_config(key, value))
            print("    -> ошибка НЕ поймана")
        except ConfigError as error:
            print(f"    -> {error}")


if __name__ == "__main__":
    main()