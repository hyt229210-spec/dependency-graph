"""Демонстрация режима обратных зависимостей на тестовых репозиториях."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graph import build_graph, format_graph, invert_repo
from testrepo import load_test_repo

DATA = Path(__file__).parent / "data"
NOBODY = "(от него никто не зависит)"

CASES = [
    ("Кто зависит от D", "basic.txt", "D", 3, ""),
    ("Кто зависит от F (цепочка вверх)", "basic.txt", "F", 10, ""),
    ("Кто зависит от F, но глубина 1", "basic.txt", "F", 1, ""),
    ("Кто зависит от A (никто)", "basic.txt", "A", 3, ""),
    ("Кто зависит от D, фильтр 'B'", "basic.txt", "D", 3, "B"),
    ("Цикл: кто зависит от A", "cycle.txt", "A", 10, ""),
]


def run_case(title, file_name, target, depth, substring):
    """Строит обратные зависимости для одного случая и печатает результат."""
    print(f"\n=== {title} (пакет: {target}, глубина: {depth}, фильтр: '{substring}')")
    reverse = invert_repo(load_test_repo(DATA / file_name))
    graph = build_graph(lambda name: reverse.get(name, []), target, depth, substring)
    for line in format_graph(graph, "<-", NOBODY):
        print("  " + line)


def main():
    """Запускает все демонстрационные случаи."""
    for case in CASES:
        run_case(*case)


if __name__ == "__main__":
    main()