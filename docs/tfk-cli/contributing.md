# Contributing to Terraformik (tfk)

Thank you for your interest in contributing to tfk! This guide will help you get started.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Coding Standards](#coding-standards)
7. [Testing](#testing)
8. [Documentation](#documentation)
9. [Pull Requests](#pull-requests)
10. [Release Process](#release-process)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Terraform 1.0+ (for integration tests)
- AWS CLI (for backend provisioner tests)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/wcampos/terraformik.git
cd terraformik

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check .
mypy terraformik
```

---

## Development Setup

### Installing Dependencies

```bash
# Install all dependencies (including dev)
pip install -e ".[dev,test,docs]"

# Or use make
make install-dev
```

### Environment Variables

Create a `.env` file for local development:

```bash
# .env
TFK_LOG_LEVEL=debug
TFC_TOKEN=your-test-token
TFC_ORGANIZATION=your-test-org
AWS_PROFILE=your-aws-profile
```

### IDE Setup

#### VS Code

Recommended extensions:
- Python
- Pylance
- Ruff
- GitLens

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

#### PyCharm

1. Set project interpreter to virtual environment
2. Enable type checking
3. Configure Ruff as external tool

---

## Project Structure

```
terraformik/
├── terraformik/              # Main package
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── cli/                  # CLI commands
│   │   ├── __init__.py
│   │   ├── main.py           # Main CLI app
│   │   └── commands/         # Command implementations
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── engine.py         # Execution engine
│   │   └── terraform.py      # Terraform wrapper
│   ├── cloud/                # Terraform Cloud integration
│   │   ├── __init__.py
│   │   ├── client.py         # API client
│   │   └── ...
│   ├── hooks/                # Hook system
│   │   ├── __init__.py
│   │   ├── manager.py        # Hook manager
│   │   └── validators/       # Built-in validators
│   ├── config/               # Configuration
│   │   ├── __init__.py
│   │   └── loader.py         # Config loading
│   ├── provisioners/         # Backend provisioners
│   ├── hcl/                  # HCL utilities
│   ├── utils/                # Utilities
│   └── exceptions/           # Custom exceptions
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── fixtures/             # Test fixtures
├── docs/                     # Documentation
├── scripts/                  # Development scripts
├── pyproject.toml            # Project configuration
├── Makefile                  # Development commands
└── README.md
```

---

## Development Workflow

### Branch Naming

Use conventional branch names:

```
feat/add-cost-estimation
fix/workspace-lock-error
docs/update-api-reference
refactor/simplify-hooks
test/add-cloud-client-tests
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add cost estimation hook
fix: handle workspace lock timeout
docs: update API reference for cloud module
refactor: simplify hook execution pipeline
test: add integration tests for cloud client
chore: update dependencies
```

### Development Commands

```bash
# Run all checks
make check

# Run specific checks
make lint        # Linting
make typecheck   # Type checking
make test        # Tests
make test-cov    # Tests with coverage

# Formatting
make format      # Format code

# Build
make build       # Build package

# Documentation
make docs        # Build docs
make docs-serve  # Serve docs locally
```

---

## Coding Standards

### Python Style

We follow PEP 8 with some modifications. Use Ruff for linting:

```bash
ruff check terraformik tests
ruff format terraformik tests
```

### Type Hints

All code should include type hints:

```python
def create_workspace(
    self,
    name: str,
    organization: str,
    description: str | None = None,
    tags: list[str] | None = None
) -> Workspace:
    """Create a new workspace."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def execute_terraform(
    self,
    command: str,
    args: list[str] | None = None,
    env: dict[str, str] | None = None
) -> ExecutionResult:
    """
    Execute a Terraform command.

    Args:
        command: The Terraform command to execute (init, plan, apply, etc.)
        args: Additional command-line arguments
        env: Environment variables to set

    Returns:
        ExecutionResult containing stdout, stderr, and exit code

    Raises:
        TerraformError: If the command fails with non-zero exit code
        TerraformNotFoundError: If Terraform binary is not found

    Example:
        >>> executor = TerraformExecutor()
        >>> result = executor.execute_terraform("init")
        >>> print(result.exit_code)
        0
    """
```

### Error Handling

Use custom exceptions:

```python
from terraformik.exceptions import TerraformError, CloudError

def get_workspace(self, name: str) -> Workspace:
    try:
        response = self._client.get(f"/workspaces/{name}")
        return Workspace.from_dict(response)
    except HTTPError as e:
        if e.response.status_code == 404:
            raise WorkspaceNotFoundError(
                f"Workspace '{name}' not found",
                details={"workspace": name}
            )
        raise CloudError(
            f"Failed to get workspace: {e}",
            status_code=e.response.status_code
        )
```

### Logging

Use the logging module:

```python
import logging

logger = logging.getLogger(__name__)

def execute(self, context: ExecutionContext) -> HookResult:
    logger.debug(f"Executing hook: {self.name}")
    try:
        result = self._run_validation(context)
        logger.info(f"Hook {self.name} completed: {result.success}")
        return result
    except Exception as e:
        logger.error(f"Hook {self.name} failed: {e}")
        raise
```

---

## Testing

### Test Structure

```
tests/
├── unit/                     # Fast, isolated tests
│   ├── test_terraform.py
│   ├── test_cloud_client.py
│   ├── test_hooks.py
│   └── test_config.py
├── integration/              # Tests with external dependencies
│   ├── test_terraform_execution.py
│   └── test_cloud_api.py
├── e2e/                      # Full workflow tests
│   └── test_full_workflow.py
├── fixtures/                 # Test data
│   ├── terraform/
│   │   ├── simple/
│   │   └── complex/
│   └── configs/
├── conftest.py               # Shared fixtures
└── __init__.py
```

### Writing Tests

Use pytest:

```python
import pytest
from terraformik.core import TerraformExecutor
from terraformik.exceptions import InitError


class TestTerraformExecutor:
    """Tests for TerraformExecutor."""

    @pytest.fixture
    def executor(self, tmp_path):
        """Create executor with temporary directory."""
        return TerraformExecutor(working_dir=tmp_path)

    def test_init_success(self, executor, terraform_fixture):
        """Test successful terraform init."""
        result = executor.init()
        assert result.success
        assert "Terraform has been successfully initialized" in result.output

    def test_init_invalid_backend(self, executor):
        """Test init with invalid backend configuration."""
        with pytest.raises(InitError) as exc_info:
            executor.init(backend_config={"bucket": "nonexistent"})
        assert "Failed to initialize backend" in str(exc_info.value)

    @pytest.mark.parametrize("version,expected", [
        ("1.5.0", True),
        ("0.12.0", False),
    ])
    def test_version_compatibility(self, executor, version, expected):
        """Test version compatibility check."""
        result = executor.check_version(version)
        assert result == expected
```

### Fixtures

```python
# conftest.py
import pytest
from pathlib import Path


@pytest.fixture
def terraform_fixture(tmp_path):
    """Create minimal Terraform configuration."""
    main_tf = tmp_path / "main.tf"
    main_tf.write_text("""
terraform {
  required_version = ">= 1.0.0"
}

variable "name" {
  type = string
}

output "greeting" {
  value = "Hello, ${var.name}!"
}
""")
    return tmp_path


@pytest.fixture
def mock_cloud_client(mocker):
    """Mock Terraform Cloud client."""
    client = mocker.Mock()
    client.list_workspaces.return_value = [
        {"name": "test-workspace", "id": "ws-123"}
    ]
    return client
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=terraformik --cov-report=html

# Run specific tests
pytest tests/unit/test_terraform.py
pytest tests/unit/test_terraform.py::TestTerraformExecutor::test_init_success

# Run by marker
pytest -m "not integration"  # Skip integration tests
pytest -m "slow"             # Run slow tests

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_large_state_file():
    """Test handling of large state files."""
    ...

@pytest.mark.integration
def test_terraform_cloud_api():
    """Test actual Terraform Cloud API."""
    ...

@pytest.mark.requires_terraform
def test_terraform_execution():
    """Test requires Terraform binary."""
    ...
```

---

## Documentation

### Building Documentation

```bash
# Build docs
make docs

# Serve locally
make docs-serve

# Open in browser
open docs/_build/html/index.html
```

### Documentation Style

Use Markdown for documentation:

```markdown
# Feature Name

Brief description of the feature.

## Usage

\`\`\`bash
tfk command --option=value
\`\`\`

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `option` | string | `default` | Description |

## Examples

### Basic Example

\`\`\`yaml
config:
  option: value
\`\`\`
```

---

## Pull Requests

### Before Submitting

1. **Update from main:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks:**
   ```bash
   make check
   ```

3. **Update documentation** if needed

4. **Add tests** for new features

### PR Template

```markdown
## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added/updated documentation
- [ ] Added/updated tests
- [ ] All checks pass
```

### Review Process

1. **Automated checks** must pass
2. **At least one approval** required
3. **Maintainer** will merge

---

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Steps

1. **Update version:**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   ```

2. **Create release PR:**
   ```bash
   git checkout -b release/v1.2.0
   git commit -m "chore: release v1.2.0"
   git push origin release/v1.2.0
   ```

3. **After merge, tag release:**
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

4. **GitHub Actions** will:
   - Build package
   - Run tests
   - Publish to PyPI
   - Create GitHub release

### Changelog Format

```markdown
# Changelog

## [1.2.0] - 2024-01-15

### Added
- Cost estimation hook (#123)
- Terraform Cloud variable sets support (#124)

### Changed
- Improved error messages for API failures (#125)

### Fixed
- Workspace lock timeout handling (#126)

### Deprecated
- Old configuration format (use v2 schema)
```

---

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/wcampos/terraformik/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wcampos/terraformik/discussions)
- **Security**: Report security issues to security@example.com

---

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](./CONTRIBUTORS.md)
- Release notes
- README acknowledgments

Thank you for contributing to tfk!
