import coverage
import unittest
import sys
import os


def main():
    # Имя текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Запускаем покрытие по всем .py в текущей директории
    cov = coverage.Coverage(
        source=[current_dir],
        omit=[
            "*run_tests_with_coverage.py",   # сам себя не тестирует
            "*test_*.py"                     # тесты не считаем
        ],
    )

    cov.start()

    # Ищем все тесты прямо здесь же
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir=current_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)

    cov.stop()
    cov.save()

    print("\n========== COVERAGE REPORT ==========")
    cov.report(show_missing=True)

    # HTML-отчёт (всегда полезно чтобы препод офигел)
    cov.html_report(directory="htmlcov")
    print("HTML report saved to htmlcov/index.html")

    # Код возврата
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
