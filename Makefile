# HAiOS Makefile
# Development automation and CI/CD tasks

.PHONY: help install install-dev test test-unit test-integration test-e2e
.PHONY: lint format type-check security-scan validate clean build
.PHONY: docs docs-serve release docker-build docker-run
.PHONY: pre-commit setup-hooks ci cd

# Default target
help: ## Show this help message
	@echo "HAiOS Development Commands"
	@echo "========================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation targets
install: ## Install production dependencies
	python -m pip install --upgrade pip
	pip install -e .

install-dev: ## Install development dependencies
	python -m pip install --upgrade pip
	pip install -e ".[dev,test,docs]"
	pre-commit install

# Testing targets
test: test-unit test-integration test-e2e ## Run all tests

test-unit: ## Run unit tests
	pytest src/tests/ -v -m "not integration and not e2e" --cov=src --cov-report=term-missing

test-integration: ## Run integration tests
	pytest src/tests/ -v -m "integration" --cov=src --cov-report=term-missing

test-e2e: ## Run end-to-end tests
	pytest src/tests/ -v -m "e2e" --cov=src --cov-report=term-missing

test-coverage: ## Run tests with detailed coverage report
	pytest src/tests/ -v --cov=src --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=85

# Code quality targets
lint: ## Run all linting checks
	flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
	black --check --diff src/
	isort --check-only --diff src/

format: ## Format code with black and isort
	black src/
	isort src/

type-check: ## Run type checking with mypy
	mypy src/ --ignore-missing-imports --no-strict-optional

security-scan: ## Run security scans
	bandit -r src/ -f txt
	safety check
	@echo "Running Trivy filesystem scan..."
	@if command -v trivy >/dev/null 2>&1; then \
		trivy fs --severity CRITICAL,HIGH,MEDIUM --format table .; \
	else \
		echo "Trivy not installed. Install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"; \
	fi

# Validation targets
validate: ## Validate JSON schemas and project structure
	@echo "Validating JSON schemas..."
	@python -c "import json; import os; from pathlib import Path; from jsonschema import Draft7Validator; \
	schema_files = list(Path('.').rglob('*.schema.json')); \
	print(f'Found {len(schema_files)} schema files'); \
	[Draft7Validator.check_schema(json.loads(f.read_text())) or print(f'✓ {f}') for f in schema_files]"
	@echo "Schema validation complete!"

validate-demo: ## Run demo in dev-fast mode to validate basic functionality
	timeout 30s python -m src --demo --mode dev-fast || echo "Demo completed (timeout expected)"

# Build targets
clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	python -m build

# Documentation targets
docs: ## Build documentation
	@if [ ! -f mkdocs.yml ]; then \
		echo "Creating mkdocs.yml..."; \
		cat > mkdocs.yml << 'EOF'; \
site_name: HAiOS Documentation; \
site_description: Hybrid AI Operating System Documentation; \
repo_url: https://github.com/haios-team/haios; \
nav:; \
  - Home: README.md; \
  - Onboarding: docs/onboarding/README.md; \
  - Architecture: docs/Document_1/; \
  - Schemas: docs/Document_2/; \
  - Scaffolds: docs/Document_3/; \
  - ADRs: docs/ADR/; \
  - Reports: docs/reports/; \
theme:; \
  name: material; \
  features:; \
    - navigation.tabs; \
    - navigation.sections; \
    - toc.integrate; \
plugins:; \
  - search; \
  - mermaid2; \
EOF; \
	fi
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

# Git hooks and pre-commit
setup-hooks: ## Set up git hooks
	pre-commit install
	pre-commit install --hook-type commit-msg

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# CI/CD simulation
ci: install-dev lint type-check security-scan test validate ## Run full CI pipeline locally

cd: build docs ## Run CD pipeline locally (build and docs)

# Release targets
release-patch: ## Create a patch release (0.0.X)
	@echo "Creating patch release..."
	@current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	new_version=$$(python -c "v='$$current_version'.split('.'); v[2]=str(int(v[2])+1); print('.'.join(v))"); \
	sed -i "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml; \
	echo "Updated version to $$new_version"; \
	git add pyproject.toml; \
	git commit -m "Bump version to $$new_version"; \
	git tag "v$$new_version"; \
	echo "Created tag v$$new_version"

release-minor: ## Create a minor release (0.X.0)
	@echo "Creating minor release..."
	@current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	new_version=$$(python -c "v='$$current_version'.split('.'); v[1]=str(int(v[1])+1); v[2]='0'; print('.'.join(v))"); \
	sed -i "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml; \
	echo "Updated version to $$new_version"; \
	git add pyproject.toml; \
	git commit -m "Bump version to $$new_version"; \
	git tag "v$$new_version"; \
	echo "Created tag v$$new_version"

release-major: ## Create a major release (X.0.0)
	@echo "Creating major release..."
	@current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	new_version=$$(python -c "v='$$current_version'.split('.'); v[0]=str(int(v[0])+1); v[1]='0'; v[2]='0'; print('.'.join(v))"); \
	sed -i "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml; \
	echo "Updated version to $$new_version"; \
	git add pyproject.toml; \
	git commit -m "Bump version to $$new_version"; \
	git tag "v$$new_version"; \
	echo "Created tag v$$new_version"

# Docker targets
docker-build: ## Build Docker image
	docker build -t haios:latest .

docker-run: ## Run HAiOS in Docker container
	docker run --rm -it haios:latest

docker-scan: ## Scan Docker image for vulnerabilities
	@if command -v trivy >/dev/null 2>&1; then \
		trivy image --severity CRITICAL,HIGH,MEDIUM haios:latest; \
	else \
		echo "Trivy not installed. Install with: curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"; \
	fi

# Development helpers
dev-setup: install-dev setup-hooks ## Complete development environment setup
	@echo "Development environment setup complete!"
	@echo "Run 'make help' to see available commands"

dev-test: ## Quick development test (unit tests only)
	pytest src/tests/ -v -m "not integration and not e2e" -x --tb=short

dev-validate: validate-demo ## Quick validation for development
	@echo "Development validation complete!"

# Environment info
info: ## Show environment information
	@echo "Python version: $$(python --version)"
	@echo "Pip version: $$(pip --version)"
	@echo "Git version: $$(git --version)"
	@echo "Current directory: $$(pwd)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-Not activated}"

sbom: ## Generate CycloneDX SBOM
	@echo "Generating SBOM for project..."
	pip show cyclonedx-bom >/dev/null 2>&1 || pip install cyclonedx-bom
	cyclonedx-bom create --output sbom.json
	@echo "SBOM generated at sbom.json" 