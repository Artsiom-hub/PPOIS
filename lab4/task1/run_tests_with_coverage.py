import coverage
import unittest
import sys
import os


def main():

    current_dir = os.path.dirname(os.path.abspath(__file__))

   
    cov = coverage.Coverage(
        source=[current_dir],
        omit=[
            "*run_tests_with_coverage.py",  
            "*test_*.py"                    
        ],
    )

    cov.start()

 
    loader = unittest.TestLoader()
    tests = loader.discover(start_dir=current_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(tests)

    cov.stop()
    cov.save()

    print("\n========== COVERAGE REPORT ==========")
    cov.report(show_missing=True)

    cov.html_report(directory="htmlcov")
    print("HTML report saved to htmlcov/index.html")

   
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main()
