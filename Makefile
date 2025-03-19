.PHONY: help install test build clean provision-cli provision-boto3 provision-all

# Default target
.DEFAULT_GOAL := help

# Variables
APP_NAME ?= myapp
ENVIRONMENT ?= dev
REGION ?= us-east-1

help: ## Display this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e ".[dev]"

test: ## Run tests
	pytest

build: ## Build the package
	python -m build

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/

provision-cli: ## Provision using AWS CLI
	@echo "Provisioning with AWS CLI for $(APP_NAME) in $(ENVIRONMENT) environment..."
	./provisioners/cli/provision.sh $(APP_NAME) $(ENVIRONMENT) $(REGION)

provision-boto3: ## Provision using Boto3
	@echo "Provisioning with Boto3 for $(APP_NAME) in $(ENVIRONMENT) environment..."
	./provisioners/boto3/provision.py --app-name $(APP_NAME) --environment $(ENVIRONMENT) --region $(REGION)

provision-all: provision-cli provision-boto3 ## Provision using both methods

# Development targets
dev-setup: install ## Set up development environment
	@echo "Development environment ready!"

dev-clean: clean ## Clean development environment
	@echo "Development environment cleaned!"

# Release targets
release-build: build ## Build release package
	@echo "Release package built!"

release-clean: clean ## Clean release artifacts
	@echo "Release artifacts cleaned!"

# Workflow targets
workflow-copy: ## Copy workflows to .github/workflows
	@echo "Copying workflows..."
	@mkdir -p .github/workflows
	@cp workflows/*.yml .github/workflows/
	@echo "Workflows copied successfully!"

# Environment-specific provisioning
provision-dev: ## Provision development environment
	@make provision-all APP_NAME=$(APP_NAME) ENVIRONMENT=dev

provision-staging: ## Provision staging environment
	@make provision-all APP_NAME=$(APP_NAME) ENVIRONMENT=staging

provision-prod: ## Provision production environment
	@make provision-all APP_NAME=$(APP_NAME) ENVIRONMENT=prod 