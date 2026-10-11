"""Построение графа зависимостей обходом в ширину (BFS) с рекурсией."""


def is_excluded(name, substring):
    """Пакет исключается, если подстрока задана и входит в его имя."""
    return bool(substring) and substring in name


class GraphBuilder:
    """Строит граф зависимостей, обходя пакеты по уровням."""

    def __init__(self, get_dependencies, max_depth, substring):
        self.get_dependencies = get_dependencies
        self.max_depth = max_depth
        self.substring = substring
        self.graph = {}
        self.seen = set()

    def build(self, root):
        """Возвращает словарь: пакет -> список его зависимостей."""
        self.seen.add(root)
        self.visit_level([root], 0)
        return self.graph

    def visit_level(self, level, depth):
        """Обрабатывает один уровень и рекурсивно переходит к следующему."""
        if not level or depth >= self.max_depth:
            return
        next_level = []
        for package in level:
            dependencies = self.allowed_dependencies(package)
            self.graph[package] = dependencies
            for dependency in dependencies:
                if dependency not in self.seen:
                    self.seen.add(dependency)
                    next_level.append(dependency)
        self.visit_level(next_level, depth + 1)

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
    """Переворачивает репозиторий: пакет -> список пакетов, зависящих от него."""
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