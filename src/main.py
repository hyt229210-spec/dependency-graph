"""Точка входа: читает конфигурацию, строит и выводит граф зависимостей."""
import argparse
import sys

from cargo import CargoError, PackageNotFound, find_direct_dependencies
from config import ConfigError, load_config
from graph import build_graph, format_graph, invert_repo
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
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="вывести обратные зависимости (только для тестового режима)",
    )
    return parser.parse_args()


def print_settings(settings):
    """Печатает параметры в формате ключ-значение."""
    print("Параметры запуска:")
    for key, value in settings.items():
        print(f"  {key}: {value}")


def make_test_getter(settings, reverse):
    """Источник зависимостей для тестового режима - файл с графом.

    При reverse вместо зависимостей возвращаются пакеты, которые зависят от данного.
    """
    repo = load_test_repo(settings["repository"])
    if settings["package_name"] not in repo:
        raise TestRepoError(
            f"Пакет '{settings['package_name']}' не найден в тестовом репозитории"
        )
    if reverse:
        repo = invert_repo(repo)
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


def run(settings, reverse):
    """Строит граф по настройкам и печатает его."""
    if reverse and not settings["test_mode"]:
        raise ConfigError(
            "Режим --reverse работает только при test_mode = true: "
            "для настоящего репозитория нет списка всех пакетов"
        )
    if settings["test_mode"]:
        getter = make_test_getter(settings, reverse)
    else:
        getter = make_real_getter(settings)
    graph = build_graph(
        getter,
        settings["package_name"],
        settings["max_depth"],
        settings["filter_substring"],
    )
    print_result(graph, settings["package_name"], reverse)


def print_result(graph, package, reverse):
    """Печатает граф зависимостей или обратные зависимости."""
    if reverse:
        print(f"Обратные зависимости пакета {package} (кто от него зависит):")
        lines = format_graph(graph, "<-", "(от него никто не зависит)")
    else:
        print(f"Граф зависимостей пакета {package}:")
        lines = format_graph(graph)
    for line in lines:
        print(f"  {line}")


def main():
    """Загружает конфигурацию и запускает построение графа."""
    args = parse_args()
    try:
        settings = load_config(args.config)
        if args.show_config:
            print_settings(settings)
        run(settings, args.reverse)
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1
    except (CargoError, TestRepoError) as error:
        print(f"Ошибка получения данных: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())