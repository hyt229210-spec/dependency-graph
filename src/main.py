"""Точка входа: читает конфигурацию, строит и выводит граф зависимостей."""
import argparse
import sys

from cargo import CargoError, PackageNotFound, find_direct_dependencies
from config import ConfigError, load_config
from graph import build_graph, format_graph
from testrepo import TestRepoError, load_test_repo


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


def make_test_getter(settings):
    """Источник зависимостей для тестового режима - файл с графом."""
    repo = load_test_repo(settings["repository"])
    if settings["package_name"] not in repo:
        raise TestRepoError(
            f"Пакет '{settings['package_name']}' не найден в тестовом репозитории"
        )
    return lambda name: repo.get(name, [])


def make_real_getter(settings):
    """Источник зависимостей для обычного режима - репозиторий на GitHub.

    Пакеты, которых нет в этом репозитории, считаются листьями графа.
    """
    repository = settings["repository"]
    root = settings["package_name"]

    def getter(name):
        try:
            return find_direct_dependencies(repository, name)
        except PackageNotFound:
            if name == root:
                raise
            return []

    return getter


def run(settings):
    """Строит граф по настройкам и печатает его."""
    if settings["test_mode"]:
        getter = make_test_getter(settings)
    else:
        getter = make_real_getter(settings)
    graph = build_graph(
        getter,
        settings["package_name"],
        settings["max_depth"],
        settings["filter_substring"],
    )
    print(f"Граф зависимостей пакета {settings['package_name']}:")
    for line in format_graph(graph):
        print(f"  {line}")


def main():
    """Загружает конфигурацию и запускает построение графа."""
    args = parse_args()
    try:
        settings = load_config(args.config)
        if args.show_config:
            print_settings(settings)
        run(settings)
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1
    except (CargoError, TestRepoError) as error:
        print(f"Ошибка получения данных: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())