"""Демонстрация построения графа на тестовых репозиториях."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graph import build_graph, format_graph
from testrepo import TestRepoError, load_test_repo

DATA = Path(__file__).parent / "data"

CASES = [
    ("Обычный граф, глубина 3", "basic.txt", "A", 3, ""),
    ("Тот же граф, но глубина 1", "basic.txt", "A", 1, ""),
    ("Глубина 10 (больше, чем есть)", "basic.txt", "A", 10, ""),
    ("Фильтр: пропускаем пакеты с 'E'", "basic.txt", "A", 10, "E"),
    ("Цикл A -> B -> C -> A", "cycle.txt", "A", 10, ""),
    ("Пакет без зависимостей", "basic.txt", "F", 3, ""),
    ("Файл с ошибкой в имени", "bad.txt", "A", 3, ""),
]


def run_case(title, file_name, root, depth, substring):
    """Строит граф для одного случая и печатает результат."""
    print(f"\n=== {title} (старт: {root}, глубина: {depth}, "
          f"фильтр: '{substring}')")
    try:
        repo = load_test_repo(DATA / file_name)
    except TestRepoError as error:
        print(f"Ошибка: {error}")
        return
    graph = build_graph(lambda name: repo.get(name, []), root, depth, substring)
    for line in format_graph(graph):
        print("  " + line)


def main():
    """Запускает все демонстрационные случаи."""
    for case in CASES:
        run_case(*case)


if __name__ == "__main__":
    main()