# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **LICENSE** – MIT license file.
- **Terraform workflow**
  - Backend config written to `backend_config.hcl` for reliable init.
  - Optional `tf_vars_file`; plan runs without `-var-file` when not provided.
  - **tfsec** security scan step (continue-on-error).
  - **Plan comment on PR** – posts plan output as a PR comment when `action` is `plan` and `GITHUB_TOKEN` is passed.
  - New input `post_plan_comment` (default: true).
- **Terraform OIDC workflow** (`workflows/terraform-oidc.yml`) – same as main workflow but uses AWS OIDC (`role-to-assume`) instead of static access keys.
- **CONTRIBUTING.md** – contribution guide (commits, PRs, dev setup).
- **Dependabot** – `.github/dependabot.yml` for GitHub Actions and Python.
- **Issue templates** – bug report and feature request (`.github/ISSUE_TEMPLATE/`).
- **Pull request template** – `.github/PULL_REQUEST_TEMPLATE.md`.
- **Tests** – pytest suite for Boto3 provisioner (`tests/test_provision.py`), validation and AWS calls mocked.
- **Package layout** – `provisioners/__init__.py` and `provisioners/boto3/__init__.py` for imports.
- **Pre-commit** – `.pre-commit-config.yaml` (Terraform fmt/validate/tfsec, Black, isort).
- **CHANGELOG.md** – this file.
- **Terraform backend module** – `modules/backend` to create S3 bucket and DynamoDB table for state (see `modules/backend/README.md`).

### Changed

- Terraform init now uses a file for backend config instead of inline string.
- Plan step supports missing or empty `tf_vars_file`.

---

## [0.1.0] – Initial release

- Reusable Terraform workflows (plan/apply, feature/main/validate).
- AWS S3 + DynamoDB backend provisioners (CLI and Boto3).
- Conventional commits and release-drafter.
- Backend and workflow documentation.

[Unreleased]: https://github.com/wcampos/terraformik/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/wcampos/terraformik/releases/tag/v0.1.0
