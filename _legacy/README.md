# HAiOS - Hybrid AI Operating System

[![CI](https://github.com/haios-team/haios/workflows/CI/badge.svg)](https://github.com/haios-team/haios/actions/workflows/ci.yml)
[![CD](https://github.com/haios-team/haios/workflows/CD/badge.svg)](https://github.com/haios-team/haios/actions/workflows/cd.yml)
[![codecov](https://codecov.io/gh/haios-team/haios/branch/main/graph/badge.svg)](https://codecov.io/gh/haios-team/haios)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An **operating-system-like orchestration layer** for AI-assisted project execution. HAiOS manages complex workflows through structured phases: **ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE**.

## 🚀 Getting Started

### For Researchers & Architects

HAiOS is currently in the **research and design phase**. To explore the architecture:

```bash
# Clone the repository
git clone https://github.com/haios-team/haios.git
cd haios

# Explore the architectural documentation
ls docs/ADR/                    # 35+ Architectural Decision Records
ls docs/schema/                 # JSON schema specifications
ls docs/appendices/             # Core principles and operational guides
```

### 📖 Recommended Reading Order

1. **[Onboarding Guide](docs/onboarding/README.md)** - Start here for project overview
2. **[ADR Index](docs/ADR/README.md)** - Browse architectural decisions by category
3. **[Recent ADRs](docs/ADR/)** - Review the 3 new proposed ADRs from third-party architectural review
4. **[Schema Directory](docs/schema/)** - Understand the formal specifications

**Note**: Installation and execution commands will be available when the project transitions from research to implementation phase.

## 📋 Features

- **Multi-Phase Orchestration**: Structured workflow management through defined phases (ANALYZE → BLUEPRINT → CONSTRUCT → VALIDATE → IDLE)
- **Schema-Driven Architecture**: Strict JSON schema validation for all control files with 35+ architectural decision records
- **Comprehensive Testing**: 85%+ test coverage with unit, integration, and E2E tests
- **Security-First Design**: Multi-layer security scanning (Bandit, Safety, Trivy) with SARIF integration
- **Cross-Platform Support**: Works on Linux, macOS, and Windows with unified tooling
- **CI/CD Ready**: Complete GitHub Actions workflows for automated testing and deployment
- **Pattern Management**: Proposed Recipe system for capturing and reusing proven implementation patterns
- **Session Continuity**: Proposed orchestration layer for persistent multi-agent workflow coordination
- **Quality Assurance**: Proposed crystallization protocol ensuring only validated knowledge enters canonical state

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
- **Schema Validation**: Ensures data integrity across all operations with comprehensive JSON schema validation

### 🔮 Proposed Architecture Enhancements

Based on comprehensive third-party architectural review, HAiOS is evolving toward:

- **Recipe Management**: Formal cookbook system for capturing and reusing proven implementation patterns across projects
- **Orchestration Layer**: Unified coordination of multi-agent workflows with persistent session state and human operator interface
- **Crystallization Protocol**: Two-space validation system separating exploratory work from canonical system state

## 🛠️ Development

**Current Phase**: Research, Design & Architecture

HAiOS is currently in the **architectural design phase**, focusing on comprehensive system design and formal specification development. The codebase represents academic research and architectural exploration rather than functional implementation.

### 🏗️ Current Development Focus

- **Architectural Decision Records (ADRs)**: 35+ formal architectural decisions with comprehensive third-party review
- **Schema Development**: Rigorous JSON schema specifications for all system components  
- **Design Validation**: Multi-perspective architectural evaluation and crystallization of core patterns
- **Research Documentation**: Extensive documentation of principles, patterns, and implementation strategies

### 🔬 Academic & Research Nature

**Important**: All code is currently **academic and non-functional**. The project serves as:
- Architectural research and design exploration
- Formal specification development  
- Pattern identification and validation
- Proof-of-concept for AI orchestration principles

### 🚀 Future Code Quality Standards

When transitioning to implementation phase, the following standards will be enforced:

- **Test Coverage**: Minimum 85% coverage required
- **Code Formatting**: Black + isort for consistent style
- **Type Checking**: MyPy for static type analysis
- **Security Scanning**: Bandit + Safety for vulnerability detection
- **Pre-commit Hooks**: Automated quality checks on every commit

## 📚 Documentation

- **[Onboarding Guide](docs/onboarding/README.md)**: Start here for new contributors
- **[Appendices A–H](docs/appendices/)**: Core principles, operational guides, scaffold template, schema directory, testing, frameworks registry, and CI/CD policy
- **[Schema Directory](docs/schema/)**: Canonical JSON-schema specifications (formerly "Document 2")
- **[ADRs](docs/ADR/)**: Architectural decision records (35 ADRs including 3 new proposed from third-party architectural review)
- **[Reports](docs/reports/)**: Progress and completion reports

### 🆕 Recent Architectural Developments

Following a comprehensive third-party architectural review, HAiOS has three new proposed ADRs addressing critical system capabilities:

- **[ADR-OS-033](docs/ADR/ADR-OS-033.md)**: **Cookbook & Recipe Management System** - Formal system for capturing and reusing proven implementation patterns
- **[ADR-OS-034](docs/ADR/ADR-OS-034.md)**: **Orchestration Layer & Session Management** - Unified multi-agent workflow coordination with persistent session state
- **[ADR-OS-035](docs/ADR/ADR-OS-035.md)**: **Crystallization Protocol & Gatekeeper Agent** - Two-space system for validating exploratory work before canonization

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

- **Phase**: Research & Architectural Design (Pre-Alpha)
- **Architecture**: 35+ ADRs with comprehensive AI architectural review underway
- **Documentation**: Extensive formal specifications and design documentation
- **Research Focus**: Academic exploration of AI orchestration principles and patterns
- **Implementation**: Planned for future phase following architectural completion

## 🤝 Contributing

### Research & Architecture Contributions

HAiOS welcomes contributions to its architectural research and design:

1. **Fork the repository**
2. **Explore the documentation**: Review ADRs, schemas, and architectural patterns
3. **Create feature branch**: `git checkout -b research/architectural-enhancement`
4. **Contribute**: 
   - Propose new ADRs following the established template
   - Enhance schema specifications
   - Improve documentation and architectural clarity
   - Provide architectural reviews and feedback
5. **Submit pull request** with detailed architectural rationale

### Research Review Checklist
- [ ] Architectural decisions are well-documented and justified
- [ ] ADRs follow the established template and governance standards
- [ ] Schema changes are backward-compatible and well-specified
- [ ] Documentation is comprehensive and technically accurate
- [ ] Contributions align with HAiOS architectural principles

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python development practices
- Inspired by operating system design principles
- Comprehensive testing and quality assurance
- Security-first development approach


**HAiOS** - Orchestrating the future of AI-assisted development 🚀 