# tfk CLI Documentation

Welcome to the Terraformik CLI (tfk) documentation. tfk is a Python CLI application for managing Terraform operations with enhanced features.

---

## Documentation Index

### Getting Started

| Document | Description |
|----------|-------------|
| [User Guide](./user-guide.md) | Complete guide to using tfk |
| [Configuration](./configuration.md) | All configuration options |

### Core Features

| Document | Description |
|----------|-------------|
| [Terraform Cloud](./terraform-cloud.md) | Terraform Cloud integration guide |
| [Hooks](./hooks.md) | Pre and post execution hooks |

### Reference

| Document | Description |
|----------|-------------|
| [API Reference](./api.md) | Python API documentation |
| [Technical Design](./technical.md) | Architecture and design document |

### Contributing

| Document | Description |
|----------|-------------|
| [Contributing Guide](./contributing.md) | How to contribute to tfk |

---

## Quick Links

### Installation

```bash
pip install terraformik
```

### Basic Usage

```bash
# Initialize
tfk init

# Plan changes
tfk plan --var-file=dev.tfvars

# Apply changes
tfk apply
```

### Get Help

```bash
tfk --help
tfk <command> --help
```

---

## Feature Overview

### Core Terraform Operations
- `tfk init` - Initialize Terraform
- `tfk plan` - Generate execution plan
- `tfk apply` - Apply changes
- `tfk destroy` - Destroy infrastructure

### Terraform Cloud Integration
- `tfk cloud login` - Authenticate
- `tfk cloud workspaces` - Manage workspaces
- `tfk cloud runs` - Trigger and monitor runs
- `tfk cloud variables` - Manage variables

### Multi-Workspace Orchestration
- `tfk multi plan` - Plan multiple workspaces
- `tfk multi apply` - Apply with dependencies
- `tfk multi status` - Check status

### Pre-Hooks System
- Format validation
- Variable validation
- Security scanning
- Cost estimation

---

## Document Map

```
docs/tfk-cli/
├── index.md              # This file
├── user-guide.md         # User guide
├── configuration.md      # Configuration reference
├── terraform-cloud.md    # Terraform Cloud guide
├── hooks.md              # Hooks reference
├── api.md                # API reference
├── technical.md          # Technical design
└── contributing.md       # Contributing guide
```

---

## Version

Documentation version: 0.1.0

Last updated: 2024
