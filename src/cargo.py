"""Получение прямых зависимостей пакета Rust (Cargo) из репозитория GitHub."""
import urllib.error
import urllib.request

try:
    import tomllib
except ImportError:  # Python старше 3.11
    tomllib = None

GITHUB_PREFIX = "https://github.com/"
RAW_HOST = "https://raw.githubusercontent.com"
TIMEOUT_SECONDS = 15
HTTP_NOT_FOUND = 404
MIN_REPO_PARTS = 2


class CargoError(Exception):
    """Ошибка получения или разбора данных о пакете."""


def raw_url(repository, file_path):
    """Строит ссылку на файл репозитория GitHub в «сыром» виде."""
    if not repository.startswith(GITHUB_PREFIX):
        raise CargoError("Поддерживаются только репозитории github.com")
    path = repository[len(GITHUB_PREFIX):].strip("/").removesuffix(".git")
    parts = path.split("/")
    if len(parts) < MIN_REPO_PARTS:
        raise CargoError(f"Не удалось разобрать адрес репозитория: {repository}")
    return f"{RAW_HOST}/{parts[0]}/{parts[1]}/HEAD/{file_path}"


def fetch_text(url):
    """Скачивает текстовый файл по ссылке. Если файла нет, возвращает None."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            return None
        raise CargoError(f"Ошибка загрузки ({error.code}): {url}")
    except (urllib.error.URLError, TimeoutError) as error:
        raise CargoError(f"Нет доступа к сети: {error}")


def parse_manifest(text):
    """Разбирает содержимое Cargo.toml в словарь."""
    if tomllib is None:
        raise CargoError("Нужен Python 3.11 или новее (модуль tomllib)")
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise CargoError(f"Не удалось разобрать Cargo.toml: {error}")


def direct_dependencies(manifest):
    """Возвращает имена из раздела [dependencies]."""
    result = []
    for key, value in manifest.get("dependencies", {}).items():
        if isinstance(value, dict) and "package" in value:
            result.append(value["package"])
        else:
            result.append(key)
    return result


def candidate_paths(package_name):
    """Места, где в репозитории может лежать Cargo.toml нужного пакета."""
    return [
        "Cargo.toml",
        f"{package_name}/Cargo.toml",
        f"crates/{package_name}/Cargo.toml",
    ]


def find_direct_dependencies(repository, package_name):
    """Ищет Cargo.toml пакета в репозитории и возвращает его прямые зависимости."""
    for path in candidate_paths(package_name):
        text = fetch_text(raw_url(repository, path))
        if text is None:
            continue
        manifest = parse_manifest(text)
        if manifest.get("package", {}).get("name") == package_name:
            return direct_dependencies(manifest)
    raise CargoError(f"Cargo.toml пакета '{package_name}' не найден в репозитории")