"""Автотесты: путь в реестре, выбор версии, зависимости и обход графа."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cargo import direct_dependencies, index_path, latest_entry
from graph import build_graph, invert_repo

BASIC = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": [],
    "E": ["F"],
    "F": [],
}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A"]}


def make_dependency(
    name, kind="normal", optional=False, package=None, target=None
):
    """Описание одной зависимости в формате реестра."""
    result = {"name": name, "kind": kind, "optional": optional}
    result["target"] = target
    if package:
        result["package"] = package
    return result


class IndexPathTests(unittest.TestCase):
    """Правило построения пути к файлу пакета в реестре."""

    def test_long_name(self):
        self.assertEqual(index_path("serde"), "se/rd/serde")

    def test_short_names(self):
        self.assertEqual(index_path("a"), "1/a")
        self.assertEqual(index_path("ab"), "2/ab")
        self.assertEqual(index_path("log"), "3/l/log")

    def test_upper_case_is_lowered(self):
        self.assertEqual(index_path("Serde"), "se/rd/serde")


class RegistryEntryTests(unittest.TestCase):
    """Выбор версии и отбор зависимостей."""

    def test_latest_skips_yanked_and_prerelease(self):
        entries = [
            {"vers": "1.0.1"},
            {"vers": "1.0.10"},
            {"vers": "1.0.11", "yanked": True},
            {"vers": "2.0.0-alpha.1"},
        ]
        self.assertEqual(latest_entry(entries)["vers"], "1.0.10")

    def test_only_normal_required_dependencies(self):
        entry = {
            "deps": [
                make_dependency("one"),
                make_dependency("opt", optional=True),
                make_dependency("dev", kind="dev"),
                make_dependency("build", kind="build"),
                make_dependency("alias", package="real"),
                make_dependency("win", target="cfg(windows)"),
                make_dependency("never", target="cfg(any())"),
                make_dependency("one"),
            ]
        }
        self.assertEqual(direct_dependencies(entry), ["one", "real"])


class GraphTests(unittest.TestCase):
    """Построение графа обходом в ширину."""

    @staticmethod
    def build(repo, root, depth, substring=""):
        getter = lambda name: repo.get(name, [])
        return build_graph(getter, root, depth, substring)

    def test_depth_limits_expansion(self):
        graph = self.build(BASIC, "A", 1)
        self.assertEqual(graph, {"A": ["B", "C"]})

    def test_full_graph(self):
        graph = self.build(BASIC, "A", 10)
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E", "F"])

    def test_filter_removes_branch(self):
        graph = self.build(BASIC, "A", 10, "E")
        self.assertNotIn("E", graph)
        self.assertNotIn("F", graph)

    def test_cycle_does_not_hang(self):
        graph = self.build(CYCLE, "A", 10)
        self.assertEqual(graph, CYCLE)

    def test_reverse_dependencies(self):
        reverse = invert_repo(BASIC)
        graph = self.build(reverse, "D", 10)
        self.assertEqual(graph["D"], ["B", "C"])


if __name__ == "__main__":
    unittest.main()