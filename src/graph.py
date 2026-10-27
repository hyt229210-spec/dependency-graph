"""Построение графа зависимостей обходом в ширину (BFS) с рекурсией."""
import sys

RECURSION_LIMIT = 20000


def is_excluded(name, substring):
    """Пакет исключается, если подстрока задана и входит в его имя."""
    return bool(substring) and substring in name


class GraphBuilder:
    """Строит граф зависимостей обходом в ширину: очередь и рекурсия."""

    def __init__(self, get_dependencies, max_depth, substring):
        """Запоминает настройки обхода и готовит пустой граф."""
        self.get_dependencies = get_dependencies
        self.max_depth = max_depth
        self.substring = substring
        self.graph = {}
        self.seen = set()

    def build(self, root):
        """Возвращает словарь: пакет -> список его зависимостей."""
        sys.setrecursionlimit(max(sys.getrecursionlimit(), RECURSION_LIMIT))
        self.seen.add(root)
        self.visit([(root, 0)])
        return self.graph

    def visit(self, queue):
        """Обрабатывает первый пакет очереди и вызывает себя для остальных.

        Зависимости пакета добавляются в конец очереди вместе с их глубиной.
        Уже встреченные пакеты повторно не добавляются, поэтому циклы
        не приводят к зависанию. Рекурсия заканчивается, когда очередь пуста.
        """
        if not queue:
            return
        package, depth = queue.pop(0)
        if depth < self.max_depth:
            dependencies = self.allowed_dependencies(package)
            self.graph[package] = dependencies
            for dependency in dependencies:
                if dependency not in self.seen:
                    self.seen.add(dependency)
                    queue.append((dependency, depth + 1))
        self.visit(queue)

    def allowed_dependencies(self, package):
        """Зависимости пакета без тех, что отсеяны фильтром."""
        return [
            name for name in self.get_dependencies(package)
            if not is_excluded(name, self.substring)
        ]


def build_graph(get_dependencies, root, max_depth, substring):
    """Строит граф зависимостей пакета root (см. GraphBuilder)."""
    return GraphBuilder(get_dependencies, max_depth, substring).build(root)


def invert_repo(repo):
    """Переворачивает репозиторий: пакет -> пакеты, зависящие от него."""
    reverse = {name: [] for name in repo}
    for package, dependencies in repo.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, []).append(package)
    return reverse


def format_graph(graph, arrow="->", empty="(нет зависимостей)"):
    """Превращает граф в строки вида 'A -> B, C'."""
    lines = []
    for package, dependencies in graph.items():
        targets = ", ".join(dependencies) if dependencies else empty
        lines.append(f"{package} {arrow} {targets}")
    return lines