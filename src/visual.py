"""Текстовые представления графа: описание PlantUML и ASCII-дерево."""

ROOT_COLOR = "#LightBlue"


def collect_nodes(graph):
    """Все пакеты графа в порядке появления (включая нераскрытые)."""
    nodes = []
    for package, dependencies in graph.items():
        for name in [package] + dependencies:
            if name not in nodes:
                nodes.append(name)
    return nodes


def to_plantuml(graph, reverse=False):
    """Строит описание графа на языке PlantUML.

    При reverse стрелки идут от зависимого пакета к тому, от кого он зависит.
    """
    nodes = collect_nodes(graph)
    root = next(iter(graph), None)
    ids = {name: f"n{index}" for index, name in enumerate(nodes)}
    lines = [
        "@startuml",
        "skinparam shadowing false",
        "left to right direction",
    ]
    for name in nodes:
        color = f" {ROOT_COLOR}" if name == root else ""
        lines.append(f'rectangle "{name}" as {ids[name]}{color}')
    for package, dependencies in graph.items():
        for dependency in dependencies:
            pair = (package, dependency)
            source, target = pair[::-1] if reverse else pair
            lines.append(f"{ids[source]} --> {ids[target]}")
    lines.append("@enduml")
    return "\n".join(lines)


def format_tree(graph, root):
    """Строит ASCII-дерево зависимостей, начиная с пакета root."""
    lines = [root]
    add_children(graph, root, "", {root}, lines)
    return lines


def add_children(graph, package, prefix, printed, lines):
    """Дописывает в lines потомков пакета; уже показанные не раскрывает."""
    children = graph.get(package, [])
    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        branch = "`-- " if is_last else "|-- "
        if child in printed:
            lines.append(f"{prefix}{branch}{child} (уже показан)")
            continue
        printed.add(child)
        lines.append(f"{prefix}{branch}{child}")
        extension = "    " if is_last else "|   "
        add_children(graph, child, prefix + extension, printed, lines)