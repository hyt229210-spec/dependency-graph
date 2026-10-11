"""Чтение файла тестового репозитория: пакеты - большие латинские буквы."""
import re

NAME_PATTERN = re.compile(r"^[A-Z]+$")


class TestRepoError(Exception):
    """Ошибка в файле тестового репозитория."""


def load_test_repo(path):
    """Читает файл вида 'A: B C' и возвращает словарь пакет -> зависимости."""
    try:
        with open(path, encoding="utf-8") as repo_file:
            lines = repo_file.readlines()
    except OSError as error:
        raise TestRepoError(
            f"Не удалось прочитать тестовый репозиторий: {error}"
        )
    repo = {}
    for number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, dependencies = parse_line(line, number)
        repo[name] = dependencies
    return repo


def parse_line(line, number):
    """Разбирает одну строку файла и проверяет имена пакетов."""
    if ":" not in line:
        raise TestRepoError(f"Строка {number}: нет двоеточия: '{line}'")
    name, _, rest = line.partition(":")
    name = name.strip()
    dependencies = rest.split()
    for item in [name] + dependencies:
        if not NAME_PATTERN.match(item):
            raise TestRepoError(
                f"Строка {number}: имя '{item}' должно состоять "
                "из больших латинских букв"
            )
    return name, dependencies