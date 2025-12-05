import os
import sys
import pytest

def main():
    # Корень проекта
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Папка с тестами
    tests_root = os.path.join(project_root, "tests")

    print("Project root:", project_root)
    print("Tests root:", tests_root)

    # Добавляем корень проекта в PYTHONPATH
    sys.path.insert(0, project_root)

    # Параметры pytest + coverage
    pytest_args = [
        tests_root,                      # где искать тесты
        "--maxfail=1",
        "--disable-warnings",

        # Coverage настройки
        f"--cov={os.path.join(project_root, 'Core_Domains')}",
        f"--cov={os.path.join(project_root, 'Infrastructure')}",
        "--cov-report=term-missing",
        f"--cov-report=html:{os.path.join(tests_root, 'htmlcov')}",

        # Файлы, которые надо исключить из покрытия
        "--cov-config=coverage.ini"
    ]

    # Запуск pytest
    exit_code = pytest.main(pytest_args)

    # Возвращаем корректный код выхода
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
