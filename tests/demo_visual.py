"""Демонстрация визуализации для трёх разных пакетов тестового репозитория."""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from graph import build_graph
from render import RenderError, render_png, save_text, show_image
from testrepo import load_test_repo
from visual import format_tree, to_plantuml

REPO_FILE = ROOT / "tests" / "data" / "basic.txt"
JAR_FILE = ROOT / "tools" / "plantuml.jar"
OUTPUT_DIR = ROOT / "output"
PACKAGES = ["A", "C", "E"]
DEPTH = 10


def visualize_package(repo, package):
    """Печатает дерево и PlantUML для пакета, затем показывает картинку."""
    graph = build_graph(lambda name: repo.get(name, []), package, DEPTH, "")
    print(f"\n=== Пакет {package}")
    print("ASCII-дерево:")
    for line in format_tree(graph, package):
        print(f"  {line}")
    puml_text = to_plantuml(graph)
    print("PlantUML:")
    print(puml_text)
    puml_path = save_text(puml_text, OUTPUT_DIR / f"demo_{package}.puml")
    try:
        show_image(render_png(puml_path, JAR_FILE))
    except RenderError as error:
        print(f"Ошибка визуализации: {error}")


def main():
    """Запускает визуализацию для всех выбранных пакетов."""
    repo = load_test_repo(REPO_FILE)
    for package in PACKAGES:
        visualize_package(repo, package)


if __name__ == "__main__":
    main()