#!/usr/bin/env python3
"""
Environment verification script for UK Tender Monitor refactor
"""
import sys
import subprocess

def check_python_version():
    """Check Python version is 3.10+"""
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 10):
        print("+ Python version meets requirements (3.10+)")
        return True
    else:
        print("- Python version too old (need 3.10+)")
        return False

def check_package(package_name):
    """Check if a package is available and get version"""
    try:
        module = __import__(package_name.replace('-', '_'))
        version = getattr(module, "__version__", "unknown")
        print(f"+ {package_name}: {version}")
        return True
    except ImportError:
        print(f"- {package_name} not installed")
        return False

def check_venv_packages():
    """Check packages in the refactor virtual environment"""
    packages = [
        "fastapi", "sqlalchemy", "alembic", "pydantic",
        "pytest", "httpx", "structlog"
    ]
    
    # Use the venv Python to check packages
    venv_python = "venv_refactor/Scripts/python.exe"
    
    all_good = True
    for package in packages:
        try:
            result = subprocess.run([
                venv_python, "-c", 
                f"import {package.replace('-', '_')}; print({package.replace('-', '_')}.__version__)"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"+ {package}: {version}")
            else:
                print(f"- {package} not installed or error")
                all_good = False
        except Exception as e:
            print(f"- {package} check failed: {e}")
            all_good = False
    
    return all_good

def main():
    """Run all environment checks"""
    print("=== Environment Verification for UK Tender Monitor Refactor ===\n")
    
    checks_passed = 0
    total_checks = 2
    
    # Check Python version
    if check_python_version():
        checks_passed += 1
    
    print()
    
    # Check virtual environment packages
    print("Checking refactor virtual environment packages:")
    if check_venv_packages():
        checks_passed += 1
    
    print(f"\n=== Summary ===")
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("SUCCESS: Environment ready for refactor!")
        return True
    else:
        print("ERROR: Environment issues found. Please fix before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)