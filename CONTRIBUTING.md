# Contributing to Terraformik

Thank you for your interest in contributing to Terraformik. This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to uphold a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when opening an issue.
- Include steps to reproduce, expected vs actual behavior, and your environment (OS, Terraform version, etc.).

### Suggesting Features

- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).
- Describe the use case and how it would benefit other users.

### Pull Requests

1. **Fork and clone** the repository.
2. **Create a branch** from `main`: `git checkout -b feat/your-feature` or `fix/your-fix`.
3. **Follow conventional commits** for commit messages (e.g. `feat: add OIDC workflow`, `fix: backend config file path`).
4. **Run checks locally**:
   - `make install` – install package and dev dependencies
   - `make test` – run tests
   - `pre-commit run --all-files` – if using pre-commit
5. **Update documentation** (README, CONTRIBUTING, or code comments) when relevant.
6. **Open a PR** using the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
7. Ensure CI passes and address any review feedback.

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation only
- `style:` formatting, no code change
- `refactor:` code change that neither fixes a bug nor adds a feature
- `test:` adding or updating tests
- `chore:` maintenance (deps, tooling, etc.)

Example: `feat(workflows): add tfsec security scan step`

### Development Setup

```bash
git clone https://github.com/wcampos/terraformik.git
cd terraformik
make install
make test
```

Optional: install [pre-commit](https://pre-commit.com/) and run `pre-commit install` to run Terraform fmt/validate and Python checks on commit.

### Project Structure

- **`.github/`** – Release Drafter config and workflow definitions used by this repo.
- **`workflows/`** – Reusable Terraform workflows for consumers to call.
- **`provisioners/`** – Scripts and tools to provision AWS backend (S3, DynamoDB).
- **`modules/`** – Terraform modules (e.g. backend bootstrap).
- **`tests/`** – Pytest tests for provisioners and utilities.

### Testing

- Run the test suite: `make test` or `pytest`.
- Add or update tests when changing behavior in provisioners or shared logic.

### Documentation

- Keep README.md accurate for setup, usage, and workflows.
- Update CHANGELOG.md (under "Unreleased") for user-facing changes when you open a PR.

## Questions?

Open a [Discussion](https://github.com/wcampos/terraformik/discussions) or an issue if something is unclear.

Thank you for contributing!
