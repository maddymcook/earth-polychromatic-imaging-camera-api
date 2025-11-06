#!/usr/bin/env python3
"""Local development script to run quality checks and tests.

This script runs the same checks that will be executed in CI/CD pipeline:
- Ruff linting and formatting
- MyPy type checking
- Pytest with coverage
- Package building

Usage:
    python dev-check.py [--fix]

Arguments:
    --fix    Automatically fix formatting and import issues
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str, fix_mode: bool = False) -> bool:
    """Run a command and return True if successful."""
    print(f"\n🔍 {description}...")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} passed")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print(f"Output:\n{e.stdout}")
        if e.stderr:
            print(f"Error:\n{e.stderr}")
        return False


def main():
    """Run all quality checks."""
    fix_mode = "--fix" in sys.argv
    root_dir = Path(__file__).parent

    print("🚀 Running local development checks...")
    print(f"Working directory: {root_dir}")

    # Change to project directory
    import os

    os.chdir(root_dir)

    # Track results
    results = []

    # Ruff formatting
    if fix_mode:
        results.append(run_command(["ruff", "format", "."], "Ruff formatting (fixing)", fix_mode))
        results.append(
            run_command(["ruff", "check", ".", "--fix"], "Ruff linting (fixing)", fix_mode)
        )
    else:
        results.append(run_command(["ruff", "format", "--check", "."], "Ruff formatting check"))
        results.append(run_command(["ruff", "check", "."], "Ruff linting check"))

    # MyPy type checking
    results.append(run_command(["mypy", "src/earth_polychromatic_api"], "MyPy type checking"))

    # Tests with coverage
    results.append(
        run_command(
            ["pytest", "--cov=earth_polychromatic_api", "--cov-report=term-missing"],
            "Pytest with coverage",
        )
    )

    # Package building
    results.append(run_command(["python", "-m", "build"], "Package building"))

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n📊 Summary: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! Ready for CI/CD pipeline.")
        sys.exit(0)
    else:
        print("💥 Some checks failed. Please fix issues before committing.")
        if not fix_mode:
            print("💡 Tip: Run 'python dev-check.py --fix' to auto-fix formatting issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
