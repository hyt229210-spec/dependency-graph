"""Точка входа: читает конфигурацию и выводит параметры."""
import argparse
import sys

from config import ConfigError, load_config


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Rust"
    )
    parser.add_argument(
        "--config", default="config.json", help="путь к JSON-файлу конфигурации"
    )
    return parser.parse_args()


def main():
    """Загружает конфигурацию и печатает параметры в формате ключ-значение."""
    args = parse_args()
    try:
        settings = load_config(args.config)
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1
    print("Параметры запуска:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())