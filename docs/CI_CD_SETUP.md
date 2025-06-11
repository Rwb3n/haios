# HAiOS CI/CD Setup Guide

This document describes the comprehensive CI/CD pipeline implemented for HAiOS, including automated testing, code quality checks, security scanning, and deployment workflows.

## Overview

The CI/CD system consists of:

- **Continuous Integration (CI)**: Automated testing, linting, and validation on every push/PR
- **Continuous Deployment (CD)**: Automated releases, package publishing, and documentation deployment
- **Local Development Tools**: Pre-commit hooks, Makefile automation, and development environment setup

## CI Pipeline (.github/workflows/ci.yml)

### Triggers
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Jobs

#### 1. Test Suite
- **Matrix Testing**: Python 3.9, 3.10, 3.11, 3.12
- **Dependency Caching**: Speeds up builds with pip cache
- **Code Quality Checks**:
  - Black formatting validation
  - isort import sorting
  - flake8 linting
  - mypy type checking
- **Test Execution**: Full test suite with coverage reporting
- **Coverage Upload**: Codecov integration for coverage tracking

#### 2. Schema Validation
- Validates all `*.schema.json` files using jsonschema
- Ensures schema compliance across the project

#### 3. End-to-End Tests
- Runs demo in dev-fast mode
- Executes E2E test scenarios
- Archives test artifacts on failure

#### 4. Security Scan
- **Bandit**: Static security analysis for Python code
- **Safety**: Checks for known vulnerabilities in dependencies
- **Trivy**: Comprehensive vulnerability scanner for:
  - Filesystem and dependency vulnerabilities
  - Configuration issues and misconfigurations
  - Container image vulnerabilities (in CD pipeline)
- **SARIF Integration**: Results uploaded to GitHub Security tab
- Generates comprehensive security reports as artifacts

#### 5. Build Check
- Validates package building with `python -m build`
- Checks package integrity with `twine check`

## CD Pipeline (.github/workflows/cd.yml)

### Triggers
- Git tags matching `v*` pattern
- Published releases

### Jobs

#### 1. Release Creation
- Generates changelog from git commits
- Creates GitHub releases with proper versioning
- Handles pre-release detection (alpha, beta, rc)

#### 2. PyPI Publishing
- Publishes stable releases to PyPI
- Skips alpha/beta releases
- Requires `PYPI_API_TOKEN` secret

#### 3. Docker Image Build
- Multi-stage Docker build for optimized images
- Pushes to GitHub Container Registry
- Semantic versioning tags
- Build cache optimization
- **Trivy container scanning**: Vulnerability assessment of built images
- Security results uploaded to GitHub Security tab

#### 4. Documentation Deployment
- Builds documentation with MkDocs
- Deploys to GitHub Pages
- Auto-generates mkdocs.yml if missing

## Local Development Tools

### Makefile Commands

```bash
# Setup and installation
make install          # Install production dependencies
make install-dev      # Install development dependencies
make dev-setup        # Complete development environment setup

# Testing
make test            # Run all tests
make test-unit       # Run unit tests only
make test-integration # Run integration tests
make test-e2e        # Run end-to-end tests
make test-coverage   # Detailed coverage report

# Code quality
make lint            # Run all linting checks
make format          # Format code with black and isort
make type-check      # Run mypy type checking
make security-scan   # Run security scans (Bandit + Safety + Trivy)

# Validation
make validate        # Validate JSON schemas
make validate-demo   # Run demo validation

# Build and release
make clean           # Clean build artifacts
make build           # Build package
make release-patch   # Create patch release
make release-minor   # Create minor release
make release-major   # Create major release

# Documentation
make docs            # Build documentation
make docs-serve      # Serve docs locally

# CI/CD simulation
make ci              # Run full CI pipeline locally
make cd              # Run CD pipeline locally

# Docker
make docker-build    # Build Docker image
make docker-run      # Run in Docker container
make docker-scan     # Scan Docker image for vulnerabilities

# Development helpers
make dev-test        # Quick unit tests
make dev-validate    # Quick validation
make info            # Show environment info
```

### Pre-commit Hooks

Automatically run on every commit:

- **Code Formatting**: Black, isort
- **Linting**: flake8, bandit
- **Type Checking**: mypy
- **File Checks**: trailing whitespace, file endings, YAML/JSON validation
- **Security**: Bandit static analysis, Trivy filesystem scanning
- **HAiOS-specific**: Schema validation, structure checks

Setup:
```bash
make setup-hooks
# or manually:
pre-commit install
```

## Configuration Files

### pyproject.toml
- Modern Python project configuration
- Tool configurations (black, isort, pytest, mypy, etc.)
- Package metadata and dependencies
- Build system configuration

### .pre-commit-config.yaml
- Pre-commit hook definitions
- Tool versions and configurations
- HAiOS-specific validations

### Dockerfile
- Multi-stage build for optimized images
- Security-focused (non-root user)
- Health checks and proper labeling

## Development Workflow

### 1. Initial Setup
```bash
git clone <repository>
cd haios
make dev-setup
```

### 2. Development Cycle
```bash
# Make changes
git add .
# Pre-commit hooks run automatically
git commit -m "feat: add new feature"
git push
```

### 3. Testing Locally
```bash
# Quick validation
make dev-test dev-validate

# Full CI simulation
make ci
```

### 4. Release Process
```bash
# Create release
make release-patch  # or release-minor, release-major
git push origin main --tags
```

## Security Tools Setup

### Trivy Installation

#### Linux/macOS
```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Verify installation
trivy --version
```

#### Windows
```powershell
# Download from GitHub releases
# https://github.com/aquasecurity/trivy/releases
# Extract and add to PATH
```

#### Docker
```bash
# Run Trivy in Docker (no installation required)
docker run --rm -v $(pwd):/workspace aquasec/trivy fs /workspace
```

### Trivy Usage Examples

```bash
# Scan filesystem for vulnerabilities
trivy fs .

# Scan Docker image
trivy image haios:latest

# Scan with specific severity levels
trivy fs --severity CRITICAL,HIGH .

# Generate SARIF report
trivy fs --format sarif --output results.sarif .

# Scan configuration files
trivy config .
```

## Environment Variables and Secrets

### Required GitHub Secrets
- `PYPI_API_TOKEN`: For PyPI publishing
- `GITHUB_TOKEN`: Automatically provided by GitHub

### Environment Variables
- `HAIOS_MODE`: Runtime mode (development, production)
- `HAIOS_LOG_LEVEL`: Logging level
- `PYTHONPATH`: Python module path

## Quality Gates

### CI Requirements
- All tests must pass (85% coverage minimum)
- No linting errors
- No security vulnerabilities
- Schema validation passes
- Type checking passes

### Code Review Requirements
- Follow error handling patterns (Section 7 of onboarding)
- Apply code review standards (Section 8 of onboarding)
- Include appropriate tests
- Update documentation if needed

## Monitoring and Observability

### Coverage Tracking
- Codecov integration for coverage reports
- HTML coverage reports in CI artifacts
- 85% minimum coverage requirement

### Security Monitoring
- **Multi-layer Security Scanning**:
  - Bandit: Python static security analysis
  - Safety: Known vulnerability detection in dependencies
  - Trivy: Comprehensive filesystem, dependency, and container scanning
- **GitHub Security Integration**: SARIF results uploaded to Security tab
- **Vulnerability Tracking**: Automated detection and reporting
- Security reports as CI artifacts with detailed findings

### Build Monitoring
- GitHub Actions status badges
- Build time tracking
- Artifact size monitoring

## Troubleshooting

### Common Issues

#### 1. Pre-commit Hook Failures
```bash
# Fix formatting issues
make format

# Update pre-commit hooks
pre-commit autoupdate
```

#### 2. Test Failures
```bash
# Run specific test
pytest src/tests/test_specific.py -v

# Debug with coverage
make test-coverage
```

#### 3. Docker Build Issues
```bash
# Build locally
make docker-build

# Check logs
docker logs <container-id>
```

#### 4. Schema Validation Errors
```bash
# Validate schemas manually
make validate

# Check specific schema
python -c "import json; from jsonschema import Draft7Validator; Draft7Validator.check_schema(json.load(open('path/to/schema.json')))"
```

## Best Practices

### 1. Commit Messages
- Use conventional commit format
- Reference issue numbers
- Keep messages concise but descriptive

### 2. Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- Feature branches: `feature/description`
- Hotfix branches: `hotfix/description`

### 3. Testing Strategy
- Unit tests for individual components
- Integration tests for component interactions
- E2E tests for user workflows
- Maintain 85%+ coverage

### 4. Security
- Regular dependency updates
- Security scanning in CI
- No secrets in code
- Use environment variables for configuration

## Future Enhancements

### Planned Improvements
- [ ] Performance benchmarking in CI
- [ ] Multi-platform Docker builds
- [ ] Automated dependency updates
- [ ] Integration with external monitoring
- [ ] Deployment to staging environments
- [ ] Load testing automation

### Monitoring Metrics
- Build success rate
- Test execution time
- Coverage trends
- Security vulnerability trends
- Release frequency 