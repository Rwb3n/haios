# HAiOS - Hybrid AI Operating System

[![CI](https://github.com/haios-team/haios/workflows/CI/badge.svg)](https://github.com/haios-team/haios/actions/workflows/ci.yml)
[![CD](https://github.com/haios-team/haios/workflows/CD/badge.svg)](https://github.com/haios-team/haios/actions/workflows/cd.yml)
[![codecov](https://codecov.io/gh/haios-team/haios/branch/main/graph/badge.svg)](https://codecov.io/gh/haios-team/haios)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An **operating-system-like orchestration layer** for AI-assisted project execution. HAiOS manages complex workflows through structured phases: **ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE**.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/haios-team/haios.git
cd haios

# Set up development environment (Linux/macOS)
make dev-setup

# Set up development environment (Windows)
.\scripts\dev.ps1 dev-setup

# Run the demo
python -m src --demo --mode dev-fast
```

## 📋 Features

- **Multi-Phase Orchestration**: Structured workflow management through defined phases
- **Schema-Driven Architecture**: Strict JSON schema validation for all control files
- **Comprehensive Testing**: 85%+ test coverage with unit, integration, and E2E tests
- **Security-First Design**: Built-in security scanning and validation
- **Cross-Platform Support**: Works on Linux, macOS, and Windows
- **CI/CD Ready**: Complete GitHub Actions workflows for automated testing and deployment

## 🏗️ Architecture

HAiOS operates through five core phases:

1. **ANALYZE**: Understand requirements and determine plan suitability
2. **BLUEPRINT**: Create detailed, decomposed project plans
3. **CONSTRUCT**: Execute tasks from the active plan
4. **VALIDATE**: Verify outputs against plans and quality standards
5. **IDLE**: Await new directives or manage human implementation

### Key Components

- **OS Control Files**: Structured `.txt` files with JSON content (state.txt, plan_*.txt, issue_*.txt)
- **Project Artifact Files**: Generated outputs using conventional extensions (.js, .css, .md, etc.)
- **Registry Map**: Central tracking of all artifacts and their relationships
- **Schema Validation**: Ensures data integrity across all operations

## 🛠️ Development

### Local Development Commands

#### Linux/macOS (Makefile)
```bash
make help              # Show all available commands
make test              # Run all tests
make lint              # Run code quality checks
make format            # Format code
make validate          # Validate schemas and structure
make build             # Build package
```

#### Windows (PowerShell)
```powershell
.\scripts\dev.ps1 help              # Show all available commands
.\scripts\dev.ps1 test              # Run all tests
.\scripts\dev.ps1 lint              # Run code quality checks
.\scripts\dev.ps1 format            # Format code
.\scripts\dev.ps1 validate          # Validate schemas and structure
.\scripts\dev.ps1 build             # Build package
```

### Code Quality Standards

- **Test Coverage**: Minimum 85% coverage required
- **Code Formatting**: Black + isort for consistent style
- **Type Checking**: MyPy for static type analysis
- **Security Scanning**: Bandit + Safety for vulnerability detection
- **Pre-commit Hooks**: Automated quality checks on every commit

### Testing Strategy

```bash
# Run specific test types
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-e2e          # End-to-end tests
make test-coverage     # Detailed coverage report
```

## 📚 Documentation

- **[Onboarding Guide](docs/onboarding/README.md)**: Start here for new contributors
- **[Appendices A–H](docs/appendices/)**: Core principles, operational guides, scaffold template, schema directory, testing, frameworks registry, and CI/CD policy
- **[Schema Directory](docs/schema/)**: Canonical JSON-schema specifications (formerly "Document 2")
- **[ADRs](docs/ADR/)**: Architectural decision records
- **[Reports](docs/reports/)**: Progress and completion reports

## 🔄 CI/CD Pipeline

### Continuous Integration
- **Multi-Python Testing**: Python 3.9, 3.10, 3.11, 3.12
- **Code Quality**: Linting, formatting, type checking
- **Multi-layer Security Scanning**: Bandit + Safety + Trivy with SARIF integration
- **Schema Validation**: Automated JSON schema verification
- **E2E Testing**: Complete workflow validation

### Continuous Deployment
- **Automated Releases**: Tag-based release creation
- **Package Publishing**: PyPI distribution for stable releases
- **Docker Images**: Multi-stage builds with Trivy security scanning
- **Documentation**: Automated deployment to GitHub Pages

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t haios:latest .

# Run in container
docker run --rm -it haios:latest python -m src --help

# Using make/PowerShell scripts
make docker-build && make docker-run
.\scripts\dev.ps1 docker-build
```

## 🔒 Security

- **Multi-layer Security Scanning**:
  - **Bandit**: Python static security analysis
  - **Safety**: Known vulnerability detection in dependencies  
  - **Trivy**: Comprehensive filesystem, dependency, and container scanning
- **GitHub Security Integration**: SARIF results in Security tab
- **Path Traversal Protection**: Built-in security validations
- **Non-root Containers**: Security-focused Docker images
- **Secret Management**: Environment variable configuration
- **Vulnerability Tracking**: Automated detection and reporting

## 📊 Project Status

- **Phase**: Alpha Development (v0.1.0)
- **Test Coverage**: 100% (42 passed, 1 skipped, 1 xfailed, 1 xpassed)
- **Code Quality**: Fully automated with pre-commit hooks
- **Documentation**: Comprehensive with auto-generated API docs

## 🤝 Contributing

1. **Fork the repository**
2. **Set up development environment**: `make dev-setup` or `.\scripts\dev.ps1 dev-setup`
3. **Create feature branch**: `git checkout -b feature/amazing-feature`
4. **Make changes** following our [error handling patterns](docs/onboarding/README.md#7-error-handling-patterns--best-practices)
5. **Run tests**: `make test` or `.\scripts\dev.ps1 test`
6. **Submit pull request**

### Code Review Checklist
- [ ] Tests pass with 85%+ coverage
- [ ] Code follows formatting standards
- [ ] Security scans pass
- [ ] Documentation updated
- [ ] Error handling patterns followed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python development practices
- Inspired by operating system design principles
- Comprehensive testing and quality assurance
- Security-first development approach

## 📞 Support

- **Documentation**: [GitHub Pages](https://haios-team.github.io/haios)
- **Issues**: [GitHub Issues](https://github.com/haios-team/haios/issues)
- **Discussions**: [GitHub Discussions](https://github.com/haios-team/haios/discussions)

---

**HAiOS** - Orchestrating the future of AI-assisted development 🚀 