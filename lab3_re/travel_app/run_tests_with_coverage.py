# run_tests_with_coverage.py
# Полный запуск тестов + покрытие всего проекта
# Работает со структурой:
# project/
#   core/
#   demo/
#   tests/
#   run_tests_with_coverage.py

import coverage
import unittest
import sys
import os


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))

    core_dir = os.path.join(project_root, "core")
    tests_dir = os.path.join(project_root, "tests")

    # --- Настройка покрытия ---
    cov = coverage.Coverage(
        source=[core_dir],  # считаем только core/
        omit=[
            "*__init__.py",
            "*run_tests_with_coverage.py",
            "*tests/*",
            "*demo/*",
        ],
    )

    cov.start()

    # --- Поиск тестов ---
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir=tests_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)

    cov.stop()
    cov.save()

    print("\n========== COVERAGE REPORT ==========")
    cov.report(show_missing=True)

    # --- HTML отчет ---
    html_dir = os.path.join(project_root, "htmlcov")
    cov.html_report(directory=html_dir)
    print(f"HTML report saved to {html_dir}/index.html")

    # Возвращаем код 0/1 (для CI)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
