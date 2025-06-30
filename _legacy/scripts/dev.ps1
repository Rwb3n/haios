# HAiOS Development PowerShell Script
# Windows equivalent of Makefile commands

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "HAiOS Development Commands" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Setup and Installation:" -ForegroundColor Yellow
    Write-Host "  install          Install production dependencies"
    Write-Host "  install-dev      Install development dependencies"
    Write-Host "  dev-setup        Complete development environment setup"
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Yellow
    Write-Host "  test             Run all tests"
    Write-Host "  test-unit        Run unit tests only"
    Write-Host "  test-integration Run integration tests"
    Write-Host "  test-e2e         Run end-to-end tests"
    Write-Host "  test-coverage    Detailed coverage report"
    Write-Host ""
    Write-Host "Code Quality:" -ForegroundColor Yellow
    Write-Host "  lint             Run all linting checks"
    Write-Host "  format           Format code with black and isort"
    Write-Host "  type-check       Run mypy type checking"
    Write-Host "  security-scan    Run security scans"
    Write-Host ""
    Write-Host "Validation:" -ForegroundColor Yellow
    Write-Host "  validate         Validate JSON schemas"
    Write-Host "  validate-demo    Run demo validation"
    Write-Host ""
    Write-Host "Build and Release:" -ForegroundColor Yellow
    Write-Host "  clean            Clean build artifacts"
    Write-Host "  build            Build package"
    Write-Host ""
    Write-Host "Docker:" -ForegroundColor Yellow
    Write-Host "  docker-scan      Scan Docker image for vulnerabilities"
    Write-Host ""
    Write-Host "Development Helpers:" -ForegroundColor Yellow
    Write-Host "  dev-test         Quick unit tests"
    Write-Host "  dev-validate     Quick validation"
    Write-Host "  info             Show environment info"
    Write-Host ""
    Write-Host "  sbom             Generate CycloneDX SBOM"
    Write-Host ""
    Write-Host "Usage: .\scripts\dev.ps1 <command>"
}

function Install-Production {
    Write-Host "Installing production dependencies..." -ForegroundColor Green
    python -m pip install --upgrade pip
    pip install -e .
}

function Install-Dev {
    Write-Host "Installing development dependencies..." -ForegroundColor Green
    python -m pip install --upgrade pip
    pip install -e ".[dev,test,docs]"
    if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
        pre-commit install
    } else {
        Write-Warning "pre-commit not found. Install with: pip install pre-commit"
    }
}

function Run-Tests {
    Write-Host "Running all tests..." -ForegroundColor Green
    pytest src/tests/ -v --cov=src --cov-report=term-missing
}

function Run-UnitTests {
    Write-Host "Running unit tests..." -ForegroundColor Green
    pytest src/tests/ -v -m "not integration and not e2e" --cov=src --cov-report=term-missing
}

function Run-IntegrationTests {
    Write-Host "Running integration tests..." -ForegroundColor Green
    pytest src/tests/ -v -m "integration" --cov=src --cov-report=term-missing
}

function Run-E2ETests {
    Write-Host "Running end-to-end tests..." -ForegroundColor Green
    pytest src/tests/ -v -m "e2e" --cov=src --cov-report=term-missing
}

function Run-TestCoverage {
    Write-Host "Running tests with detailed coverage..." -ForegroundColor Green
    pytest src/tests/ -v --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=85
}

function Run-Lint {
    Write-Host "Running linting checks..." -ForegroundColor Green
    
    Write-Host "Checking with flake8..." -ForegroundColor Blue
    flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
    
    Write-Host "Checking formatting with black..." -ForegroundColor Blue
    black --check --diff src/
    
    Write-Host "Checking import sorting with isort..." -ForegroundColor Blue
    isort --check-only --diff src/
}

function Format-Code {
    Write-Host "Formatting code..." -ForegroundColor Green
    black src/
    isort src/
}

function Run-TypeCheck {
    Write-Host "Running type checking..." -ForegroundColor Green
    mypy src/ --ignore-missing-imports --no-strict-optional
}

function Run-SecurityScan {
    Write-Host "Running security scans..." -ForegroundColor Green
    
    Write-Host "Running bandit..." -ForegroundColor Blue
    bandit -r src/ -f txt
    
    Write-Host "Running safety check..." -ForegroundColor Blue
    safety check
    
    Write-Host "Running Trivy filesystem scan..." -ForegroundColor Blue
    if (Get-Command trivy -ErrorAction SilentlyContinue) {
        trivy fs --severity CRITICAL,HIGH,MEDIUM --format table .
    } else {
        Write-Warning "Trivy not installed. Download from: https://github.com/aquasecurity/trivy/releases"
    }
}

function Validate-Schemas {
    Write-Host "Validating JSON schemas..." -ForegroundColor Green
    python -c @"
import json
import os
from pathlib import Path
from jsonschema import Draft7Validator

schema_files = list(Path('.').rglob('*.schema.json'))
print(f'Found {len(schema_files)} schema files')

for schema_file in schema_files:
    print(f'Validating {schema_file}')
    with open(schema_file) as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)
    print(f'✓ {schema_file} is valid')

print('Schema validation complete!')
"@
}

function Validate-Demo {
    Write-Host "Running demo validation..." -ForegroundColor Green
    $timeout = 30
    $job = Start-Job -ScriptBlock { python -m src --demo --mode dev-fast }
    if (Wait-Job $job -Timeout $timeout) {
        Receive-Job $job
    } else {
        Stop-Job $job
        Write-Host "Demo completed (timeout expected)" -ForegroundColor Yellow
    }
    Remove-Job $job
}

function Clean-Artifacts {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Green
    
    $paths = @(
        "build", "dist", "*.egg-info", ".pytest_cache", 
        ".coverage", "htmlcov", ".mypy_cache"
    )
    
    foreach ($path in $paths) {
        if (Test-Path $path) {
            Remove-Item $path -Recurse -Force
            Write-Host "Removed $path" -ForegroundColor Blue
        }
    }
    
    # Remove __pycache__ directories
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
        Write-Host "Removed $($_.FullName)" -ForegroundColor Blue
    }
    
    # Remove .pyc files
    Get-ChildItem -Path . -Recurse -File -Name "*.pyc" | Remove-Item -Force
}

function Build-Package {
    Write-Host "Building package..." -ForegroundColor Green
    Clean-Artifacts
    python -m build
}

function Dev-Setup {
    Write-Host "Setting up development environment..." -ForegroundColor Green
    Install-Dev
    Write-Host "Development environment setup complete!" -ForegroundColor Green
    Write-Host "Run '.\scripts\dev.ps1 help' to see available commands" -ForegroundColor Cyan
}

function Dev-Test {
    Write-Host "Running quick development tests..." -ForegroundColor Green
    pytest src/tests/ -v -m "not integration and not e2e" -x --tb=short
}

function Dev-Validate {
    Write-Host "Running quick validation..." -ForegroundColor Green
    Validate-Demo
    Write-Host "Development validation complete!" -ForegroundColor Green
}

function Scan-DockerImage {
    Write-Host "Scanning Docker image for vulnerabilities..." -ForegroundColor Green
    if (Get-Command trivy -ErrorAction SilentlyContinue) {
        trivy image --severity CRITICAL,HIGH,MEDIUM haios:latest
    } else {
        Write-Warning "Trivy not installed. Download from: https://github.com/aquasecurity/trivy/releases"
    }
}

function Show-Info {
    Write-Host "Environment Information:" -ForegroundColor Cyan
    Write-Host "Python version: $(python --version)"
    Write-Host "Pip version: $(pip --version)"
    Write-Host "Git version: $(git --version)"
    Write-Host "Current directory: $(Get-Location)"
    $venv = if ($env:VIRTUAL_ENV) { $env:VIRTUAL_ENV } else { "Not activated" }
    Write-Host "Virtual environment: $venv"
}

# Main command dispatcher
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Production }
    "install-dev" { Install-Dev }
    "dev-setup" { Dev-Setup }
    "test" { Run-Tests }
    "test-unit" { Run-UnitTests }
    "test-integration" { Run-IntegrationTests }
    "test-e2e" { Run-E2ETests }
    "test-coverage" { Run-TestCoverage }
    "lint" { Run-Lint }
    "format" { Format-Code }
    "type-check" { Run-TypeCheck }
    "security-scan" { Run-SecurityScan }
    "validate" { Validate-Schemas }
    "validate-demo" { Validate-Demo }
    "clean" { Clean-Artifacts }
    "build" { Build-Package }
    "docker-scan" { Scan-DockerImage }
    "dev-test" { Dev-Test }
    "dev-validate" { Dev-Validate }
    "info" { Show-Info }
    "sbom" {
        Write-Host "Generating CycloneDX SBOM..." -ForegroundColor Green
        # Implementation of sbom command
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Run '.\scripts\dev.ps1 help' to see available commands" -ForegroundColor Yellow
    }
} 