"""Точка входа: читает конфигурацию, строит и выводит граф зависимостей."""
import argparse
import sys

from cargo import CargoError, PackageNotFound, find_direct_dependencies
from config import ConfigError, load_config
from graph import build_graph, format_graph, invert_repo
from render import RenderError, render_png, save_text, show_image
from testrepo import TestRepoError, load_test_repo
from visual import format_tree, to_plantuml


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
    parser.add_argument(
        "--image", action="store_true", help="построить и показать изображение графа"
    )
    parser.add_argument(
        "--jar", default="tools/plantuml.jar", help="путь к plantuml.jar"
    )
    parser.add_argument(
        "--out", default="output/graph.puml", help="куда сохранить описание PlantUML"
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


def run(settings, args):
    """Строит граф по настройкам, печатает его и при необходимости рисует."""
    if args.reverse and not settings["test_mode"]:
        raise ConfigError(
            "Режим --reverse работает только при test_mode = true: "
            "для настоящего репозитория нет списка всех пакетов"
        )
    if settings["test_mode"]:
        getter = make_test_getter(settings, args.reverse)
    else:
        getter = make_real_getter(settings)
    graph = build_graph(
        getter,
        settings["package_name"],
        settings["max_depth"],
        settings["filter_substring"],
    )
    print_result(graph, settings, args.reverse)
    if args.image:
        visualize(graph, args)


def print_result(graph, settings, reverse):
    """Печатает граф зависимостей (или обратные зависимости) и, если нужно, дерево."""
    package = settings["package_name"]
    if reverse:
        print(f"Обратные зависимости пакета {package} (кто от него зависит):")
        lines = format_graph(graph, "<-", "(от него никто не зависит)")
    else:
        print(f"Граф зависимостей пакета {package}:")
        lines = format_graph(graph)
    for line in lines:
        print(f"  {line}")
    if settings["ascii_tree"]:
        print("\nASCII-дерево:")
        for line in format_tree(graph, package):
            print(f"  {line}")


def visualize(graph, args):
    """Формирует описание PlantUML, строит изображение и показывает его."""
    puml_text = to_plantuml(graph, args.reverse)
    print("\nОписание графа на языке PlantUML:")
    print(puml_text)
    puml_path = save_text(puml_text, args.out)
    png_path = render_png(puml_path, args.jar)
    print(f"\nИзображение сохранено: {png_path}")
    show_image(png_path)


def main():
    """Загружает конфигурацию и запускает построение графа."""
    args = parse_args()
    try:
        settings = load_config(args.config)
        if args.show_config:
            print_settings(settings)
        run(settings, args)
    except ConfigError as error:
        print(f"Ошибка конфигурации: {error}")
        return 1
    except (CargoError, TestRepoError) as error:
        print(f"Ошибка получения данных: {error}")
        return 1
    except RenderError as error:
        print(f"Ошибка визуализации: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())