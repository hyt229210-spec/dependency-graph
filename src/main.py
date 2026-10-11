"""Точка входа: читает конфигурацию и выводит прямые зависимости пакета."""
import argparse
import sys

from cargo import CargoError, find_direct_dependencies
from config import ConfigError, load_config


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Rust"
    )
    parser.add_argument(
        "--config", default="config.json", help="путь к JSON-файлу конфигурации"
    )
    parser.add_argument(
        "--show-config", action="store_true", help="вывести параметры конфигурации"
    )
    return parser.parse_args()


def print_settings(settings):
    """Печатает параметры в формате ключ-значение."""
    print("Параметры запуска:")
    for key, value in settings.items():
        print(f"  {key}: {value}")


def main():
    """Загружает конфигурацию и печатает прямые зависимости пакета."""
    args = parse_args()
    try:
        settings = load_config(args.config)
        if args.show_config:
            print_settings(settings)
        if settings["test_mode"]:
            print("Тестовый режим будет добавлен на этапе 3.")
            return 0
        dependencies = find_direct_dependencies(
            settings["repository"], settings["package_name"]
        )
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1
    except CargoError as error:
        print(f"Ошибка получения данных: {error}")
        return 1
    print(f"Прямые зависимости пакета {settings['package_name']}:")
    for name in dependencies:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())