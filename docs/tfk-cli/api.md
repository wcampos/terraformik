# tfk API Reference

Complete API reference for the Terraformik CLI (tfk) Python modules.

---

## Table of Contents

1. [Core Module](#core-module)
2. [Cloud Module](#cloud-module)
3. [Hooks Module](#hooks-module)
4. [Config Module](#config-module)
5. [Provisioners Module](#provisioners-module)
6. [HCL Module](#hcl-module)
7. [Exceptions](#exceptions)
8. [Type Definitions](#type-definitions)

---

## Core Module

### `terraformik.core.terraform`

The main Terraform execution wrapper.

#### `TerraformExecutor`

```python
class TerraformExecutor:
    """
    Wrapper for executing Terraform commands.

    Provides a Pythonic interface for all Terraform CLI operations
    with enhanced error handling and output parsing.

    Attributes:
        working_dir: Path to the Terraform working directory
        terraform_path: Path to the Terraform binary
        env: Environment variables for Terraform execution
    """

    def __init__(
        self,
        working_dir: Path | str = ".",
        terraform_path: str = "terraform",
        env: dict[str, str] | None = None
    ) -> None:
        """
        Initialize the Terraform executor.

        Args:
            working_dir: Working directory for Terraform operations
            terraform_path: Path to Terraform binary (default: "terraform")
            env: Additional environment variables

        Raises:
            TerraformNotFoundError: If Terraform binary is not found
        """
```

##### `init()`

```python
def init(
    self,
    backend_config: dict[str, str] | Path | None = None,
    reconfigure: bool = False,
    upgrade: bool = False,
    migrate_state: bool = False,
    lock: bool = True,
    lock_timeout: str = "0s"
) -> InitResult:
    """
    Initialize a Terraform working directory.

    Downloads providers, initializes backend, and prepares the
    working directory for other commands.

    Args:
        backend_config: Backend configuration as dict or path to file
        reconfigure: Reconfigure backend, ignoring saved configuration
        upgrade: Upgrade modules and plugins to latest versions
        migrate_state: Migrate state to new backend
        lock: Lock state during operation
        lock_timeout: Duration to retry state lock

    Returns:
        InitResult with success status and output

    Raises:
        InitError: If initialization fails

    Example:
        >>> executor = TerraformExecutor("./infrastructure")
        >>> result = executor.init(
        ...     backend_config={"bucket": "my-bucket"},
        ...     upgrade=True
        ... )
        >>> print(result.success)
        True
    """
```

##### `plan()`

```python
def plan(
    self,
    var_file: Path | str | None = None,
    variables: dict[str, Any] | None = None,
    out: Path | str | None = None,
    target: list[str] | None = None,
    destroy: bool = False,
    refresh: bool = True,
    refresh_only: bool = False,
    parallelism: int = 10,
    detailed_exitcode: bool = True
) -> PlanResult:
    """
    Generate a Terraform execution plan.

    Creates a plan showing what actions Terraform will take to
    change the infrastructure to match the configuration.

    Args:
        var_file: Path to variable definitions file (.tfvars)
        variables: Variables as a dictionary
        out: Path to save the plan file
        target: List of resources to target
        destroy: Create a destroy plan
        refresh: Update state before planning
        refresh_only: Only refresh state, don't plan changes
        parallelism: Limit concurrent operations
        detailed_exitcode: Return detailed exit codes

    Returns:
        PlanResult with plan details and changes summary

    Raises:
        PlanError: If planning fails

    Example:
        >>> result = executor.plan(
        ...     var_file="dev.tfvars",
        ...     out="plan.tfplan"
        ... )
        >>> print(f"Changes: {result.changes.add} to add")
        Changes: 5 to add
    """
```

##### `apply()`

```python
def apply(
    self,
    plan_file: Path | str | None = None,
    var_file: Path | str | None = None,
    variables: dict[str, Any] | None = None,
    target: list[str] | None = None,
    auto_approve: bool = False,
    parallelism: int = 10,
    refresh: bool = True
) -> ApplyResult:
    """
    Apply Terraform changes.

    Executes the actions proposed in a Terraform plan to create,
    update, or delete infrastructure.

    Args:
        plan_file: Path to saved plan file
        var_file: Path to variable definitions file
        variables: Variables as a dictionary
        target: List of resources to target
        auto_approve: Skip interactive approval
        parallelism: Limit concurrent operations
        refresh: Update state before applying

    Returns:
        ApplyResult with applied changes summary

    Raises:
        ApplyError: If apply fails

    Example:
        >>> result = executor.apply(
        ...     plan_file="plan.tfplan",
        ...     auto_approve=True
        ... )
        >>> print(f"Applied: {result.changes.add} added")
        Applied: 5 added
    """
```

##### `destroy()`

```python
def destroy(
    self,
    var_file: Path | str | None = None,
    variables: dict[str, Any] | None = None,
    target: list[str] | None = None,
    auto_approve: bool = False,
    parallelism: int = 10
) -> DestroyResult:
    """
    Destroy Terraform-managed infrastructure.

    Args:
        var_file: Path to variable definitions file
        variables: Variables as a dictionary
        target: List of resources to target
        auto_approve: Skip interactive approval
        parallelism: Limit concurrent operations

    Returns:
        DestroyResult with destroyed resources summary

    Raises:
        DestroyError: If destroy fails
    """
```

##### `fmt()`

```python
def fmt(
    self,
    path: Path | str = ".",
    recursive: bool = False,
    check: bool = False,
    diff: bool = False,
    write: bool = True
) -> FmtResult:
    """
    Format Terraform configuration files.

    Args:
        path: Path to format (file or directory)
        recursive: Process directories recursively
        check: Check if files are formatted (don't modify)
        diff: Show diff of formatting changes
        write: Write formatting changes to files

    Returns:
        FmtResult with list of modified/unformatted files
    """
```

##### `validate()`

```python
def validate(
    self,
    json_output: bool = False
) -> ValidateResult:
    """
    Validate Terraform configuration.

    Args:
        json_output: Return result as JSON

    Returns:
        ValidateResult with validation status and diagnostics
    """
```

##### `output()`

```python
def output(
    self,
    name: str | None = None,
    json_output: bool = False,
    raw: bool = False
) -> OutputResult:
    """
    Read Terraform output values.

    Args:
        name: Specific output to read (None for all)
        json_output: Return as JSON
        raw: Return raw value without quotes

    Returns:
        OutputResult with output values
    """
```

##### `workspace_list()`

```python
def workspace_list(self) -> list[Workspace]:
    """
    List available workspaces.

    Returns:
        List of Workspace objects with name and current status
    """
```

##### `workspace_select()`

```python
def workspace_select(self, name: str) -> None:
    """
    Select a workspace.

    Args:
        name: Workspace name to select

    Raises:
        WorkspaceError: If workspace doesn't exist
    """
```

##### `workspace_new()`

```python
def workspace_new(self, name: str) -> Workspace:
    """
    Create and select a new workspace.

    Args:
        name: Name for the new workspace

    Returns:
        Created Workspace object

    Raises:
        WorkspaceError: If workspace already exists
    """
```

##### `workspace_delete()`

```python
def workspace_delete(self, name: str, force: bool = False) -> None:
    """
    Delete a workspace.

    Args:
        name: Workspace to delete
        force: Force deletion even if state exists

    Raises:
        WorkspaceError: If workspace is current or has resources
    """
```

---

### `terraformik.core.engine`

The core execution engine.

#### `ExecutionEngine`

```python
class ExecutionEngine:
    """
    Core engine for orchestrating Terraform operations.

    Coordinates between configuration, hooks, and Terraform execution.
    """

    def __init__(
        self,
        config: TfkConfig,
        terraform: TerraformExecutor | None = None,
        hook_manager: HookManager | None = None
    ) -> None:
        """
        Initialize the execution engine.

        Args:
            config: tfk configuration
            terraform: Terraform executor instance
            hook_manager: Hook manager instance
        """
```

##### `execute()`

```python
def execute(
    self,
    command: Command,
    options: CommandOptions,
    run_hooks: bool = True
) -> ExecutionResult:
    """
    Execute a Terraform command with hooks.

    Args:
        command: Command to execute (init, plan, apply, etc.)
        options: Command options
        run_hooks: Whether to run pre/post hooks

    Returns:
        ExecutionResult with command output and status

    Example:
        >>> engine = ExecutionEngine(config)
        >>> result = engine.execute(
        ...     Command.PLAN,
        ...     PlanOptions(var_file="dev.tfvars"),
        ...     run_hooks=True
        ... )
    """
```

---

## Cloud Module

### `terraformik.cloud.client`

Terraform Cloud API client.

#### `TerraformCloudClient`

```python
class TerraformCloudClient:
    """
    Client for Terraform Cloud/Enterprise API.

    Provides methods for managing workspaces, runs, variables,
    and state through the Terraform Cloud API.

    Attributes:
        organization: Terraform Cloud organization name
        base_url: API base URL
    """

    BASE_URL = "https://app.terraform.io/api/v2"

    def __init__(
        self,
        token: str,
        organization: str,
        base_url: str | None = None,
        timeout: float = 30.0
    ) -> None:
        """
        Initialize the Terraform Cloud client.

        Args:
            token: API authentication token
            organization: Organization name
            base_url: API base URL (for TFE)
            timeout: Request timeout in seconds

        Raises:
            AuthenticationError: If token is invalid
        """
```

#### Workspace Methods

##### `list_workspaces()`

```python
def list_workspaces(
    self,
    search: str | None = None,
    page_size: int = 20,
    page_number: int = 1
) -> PaginatedResponse[Workspace]:
    """
    List workspaces in the organization.

    Args:
        search: Search query for workspace names
        page_size: Number of results per page
        page_number: Page number to retrieve

    Returns:
        Paginated list of Workspace objects

    Example:
        >>> client = TerraformCloudClient(token, "my-org")
        >>> workspaces = client.list_workspaces(search="prod")
        >>> for ws in workspaces.data:
        ...     print(ws.name)
    """
```

##### `get_workspace()`

```python
def get_workspace(self, name: str) -> Workspace:
    """
    Get workspace by name.

    Args:
        name: Workspace name

    Returns:
        Workspace object

    Raises:
        WorkspaceNotFoundError: If workspace doesn't exist
    """
```

##### `create_workspace()`

```python
def create_workspace(
    self,
    name: str,
    description: str | None = None,
    execution_mode: ExecutionMode = ExecutionMode.REMOTE,
    auto_apply: bool = False,
    terraform_version: str | None = None,
    working_directory: str | None = None,
    vcs_repo: VCSRepoConfig | None = None,
    tags: list[str] | None = None
) -> Workspace:
    """
    Create a new workspace.

    Args:
        name: Workspace name
        description: Workspace description
        execution_mode: Execution mode (remote, local, agent)
        auto_apply: Auto-apply successful plans
        terraform_version: Terraform version constraint
        working_directory: Terraform working directory
        vcs_repo: VCS repository configuration
        tags: Workspace tags

    Returns:
        Created Workspace object

    Raises:
        WorkspaceExistsError: If workspace already exists
    """
```

##### `update_workspace()`

```python
def update_workspace(
    self,
    workspace_id: str,
    **kwargs
) -> Workspace:
    """
    Update workspace settings.

    Args:
        workspace_id: Workspace ID
        **kwargs: Fields to update (same as create_workspace)

    Returns:
        Updated Workspace object
    """
```

##### `delete_workspace()`

```python
def delete_workspace(self, name: str) -> None:
    """
    Delete a workspace.

    Args:
        name: Workspace name

    Raises:
        WorkspaceNotFoundError: If workspace doesn't exist
    """
```

#### Run Methods

##### `list_runs()`

```python
def list_runs(
    self,
    workspace_id: str,
    status: RunStatus | None = None,
    page_size: int = 20
) -> PaginatedResponse[Run]:
    """
    List runs for a workspace.

    Args:
        workspace_id: Workspace ID
        status: Filter by run status
        page_size: Results per page

    Returns:
        Paginated list of Run objects
    """
```

##### `get_run()`

```python
def get_run(self, run_id: str) -> Run:
    """
    Get run details.

    Args:
        run_id: Run ID

    Returns:
        Run object with full details
    """
```

##### `create_run()`

```python
def create_run(
    self,
    workspace_id: str,
    message: str | None = None,
    auto_apply: bool = False,
    is_destroy: bool = False,
    target_addrs: list[str] | None = None,
    replace_addrs: list[str] | None = None,
    refresh: bool = True,
    refresh_only: bool = False
) -> Run:
    """
    Create and queue a new run.

    Args:
        workspace_id: Workspace ID
        message: Run message/description
        auto_apply: Auto-apply if plan succeeds
        is_destroy: Create destroy run
        target_addrs: Target specific resources
        replace_addrs: Resources to replace
        refresh: Refresh state before planning
        refresh_only: Only refresh state

    Returns:
        Created Run object

    Example:
        >>> run = client.create_run(
        ...     workspace_id="ws-abc123",
        ...     message="Deploy v1.2.3",
        ...     auto_apply=False
        ... )
        >>> print(run.id)
        run-xyz789
    """
```

##### `apply_run()`

```python
def apply_run(
    self,
    run_id: str,
    comment: str | None = None
) -> Run:
    """
    Apply a planned run.

    Args:
        run_id: Run ID
        comment: Apply comment

    Returns:
        Updated Run object

    Raises:
        RunError: If run is not in applyable state
    """
```

##### `discard_run()`

```python
def discard_run(
    self,
    run_id: str,
    comment: str | None = None
) -> Run:
    """
    Discard a planned run.

    Args:
        run_id: Run ID
        comment: Discard comment

    Returns:
        Updated Run object
    """
```

##### `cancel_run()`

```python
def cancel_run(
    self,
    run_id: str,
    comment: str | None = None,
    force: bool = False
) -> Run:
    """
    Cancel an in-progress run.

    Args:
        run_id: Run ID
        comment: Cancel comment
        force: Force cancel (may leave resources in unknown state)

    Returns:
        Updated Run object
    """
```

##### `wait_for_run()`

```python
def wait_for_run(
    self,
    run_id: str,
    target_statuses: list[RunStatus] | None = None,
    timeout: float = 3600,
    poll_interval: float = 5.0,
    callback: Callable[[Run], None] | None = None
) -> Run:
    """
    Wait for run to reach target status.

    Args:
        run_id: Run ID
        target_statuses: Statuses to wait for (default: terminal states)
        timeout: Maximum wait time in seconds
        poll_interval: Polling interval in seconds
        callback: Called on each poll with current run

    Returns:
        Final Run object

    Raises:
        TimeoutError: If timeout exceeded
    """
```

#### Variable Methods

##### `list_variables()`

```python
def list_variables(
    self,
    workspace_id: str
) -> list[Variable]:
    """
    List workspace variables.

    Args:
        workspace_id: Workspace ID

    Returns:
        List of Variable objects
    """
```

##### `create_variable()`

```python
def create_variable(
    self,
    workspace_id: str,
    key: str,
    value: str,
    category: VariableCategory = VariableCategory.TERRAFORM,
    description: str | None = None,
    sensitive: bool = False,
    hcl: bool = False
) -> Variable:
    """
    Create a workspace variable.

    Args:
        workspace_id: Workspace ID
        key: Variable key/name
        value: Variable value
        category: Variable category (terraform or env)
        description: Variable description
        sensitive: Mark as sensitive (write-only)
        hcl: Parse value as HCL

    Returns:
        Created Variable object
    """
```

##### `update_variable()`

```python
def update_variable(
    self,
    variable_id: str,
    **kwargs
) -> Variable:
    """
    Update a variable.

    Args:
        variable_id: Variable ID
        **kwargs: Fields to update

    Returns:
        Updated Variable object
    """
```

##### `delete_variable()`

```python
def delete_variable(self, variable_id: str) -> None:
    """
    Delete a variable.

    Args:
        variable_id: Variable ID
    """
```

#### State Methods

##### `get_current_state()`

```python
def get_current_state(
    self,
    workspace_id: str
) -> StateVersion:
    """
    Get current state version.

    Args:
        workspace_id: Workspace ID

    Returns:
        Current StateVersion object
    """
```

##### `list_state_versions()`

```python
def list_state_versions(
    self,
    workspace_id: str,
    page_size: int = 20
) -> PaginatedResponse[StateVersion]:
    """
    List state versions.

    Args:
        workspace_id: Workspace ID
        page_size: Results per page

    Returns:
        Paginated list of StateVersion objects
    """
```

##### `download_state()`

```python
def download_state(
    self,
    state_version_id: str
) -> dict:
    """
    Download state file contents.

    Args:
        state_version_id: State version ID

    Returns:
        State file as dictionary
    """
```

##### `create_state_version()`

```python
def create_state_version(
    self,
    workspace_id: str,
    state: dict,
    serial: int | None = None,
    md5: str | None = None,
    lineage: str | None = None,
    force: bool = False
) -> StateVersion:
    """
    Upload a new state version.

    Args:
        workspace_id: Workspace ID
        state: State file contents
        serial: State serial number
        md5: MD5 hash of state
        lineage: State lineage
        force: Force upload even if serial mismatch

    Returns:
        Created StateVersion object
    """
```

---

## Hooks Module

### `terraformik.hooks.manager`

Hook execution management.

#### `HookManager`

```python
class HookManager:
    """
    Manages execution of pre and post hooks.

    Coordinates hook discovery, registration, and execution
    for Terraform operations.
    """

    def __init__(
        self,
        config: HookConfig,
        registry: HookRegistry | None = None
    ) -> None:
        """
        Initialize the hook manager.

        Args:
            config: Hook configuration
            registry: Hook registry (default: built-in hooks)
        """
```

##### `run_hooks()`

```python
def run_hooks(
    self,
    hook_type: HookType,
    context: ExecutionContext
) -> HookResult:
    """
    Run all hooks of a given type.

    Args:
        hook_type: Type of hooks to run (pre_init, pre_plan, etc.)
        context: Execution context with state and config

    Returns:
        HookResult with aggregated results

    Example:
        >>> manager = HookManager(config)
        >>> result = manager.run_hooks(
        ...     HookType.PRE_PLAN,
        ...     context
        ... )
        >>> if not result.success:
        ...     print(f"Hook failed: {result.message}")
    """
```

##### `register_hook()`

```python
def register_hook(
    self,
    hook: Hook | type[Hook],
    hook_type: HookType | None = None
) -> None:
    """
    Register a custom hook.

    Args:
        hook: Hook instance or class
        hook_type: Override hook type (optional)
    """
```

##### `list_hooks()`

```python
def list_hooks(
    self,
    hook_type: HookType | None = None
) -> list[HookInfo]:
    """
    List registered hooks.

    Args:
        hook_type: Filter by hook type (optional)

    Returns:
        List of HookInfo objects
    """
```

### `terraformik.hooks.base`

Base hook classes.

#### `Hook`

```python
class Hook(ABC):
    """
    Abstract base class for hooks.

    Subclass this to create custom hooks.

    Attributes:
        name: Hook identifier
        description: Human-readable description
        hook_type: When the hook runs
        fail_on_error: Whether failure stops execution
    """

    name: str
    description: str = ""
    hook_type: HookType
    fail_on_error: bool = True

    @abstractmethod
    def execute(
        self,
        context: ExecutionContext
    ) -> HookResult:
        """
        Execute the hook logic.

        Args:
            context: Execution context

        Returns:
            HookResult indicating success/failure
        """
```

#### `ExecutionContext`

```python
@dataclass
class ExecutionContext:
    """
    Context passed to hooks during execution.

    Attributes:
        command: Current command being executed
        working_dir: Terraform working directory
        config: tfk configuration
        terraform: Terraform executor
        state: Current Terraform state (if available)
        plan: Terraform plan (for post_plan, pre_apply)
        variables: Resolved variables
    """

    command: Command
    working_dir: Path
    config: TfkConfig
    terraform: TerraformExecutor
    state: dict | None = None
    plan: TerraformPlan | None = None
    variables: dict[str, Any] = field(default_factory=dict)

    def get_state(self) -> dict:
        """Get current state, loading if necessary."""

    def get_plan(self) -> TerraformPlan | None:
        """Get current plan if available."""

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable value."""
```

#### `HookResult`

```python
@dataclass
class HookResult:
    """
    Result of hook execution.

    Attributes:
        success: Whether hook succeeded
        message: Human-readable message
        data: Additional data from hook
        duration: Execution duration
    """

    success: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
```

### Built-in Hooks

#### `terraformik.hooks.validators.format`

```python
class FormatCheckHook(Hook):
    """
    Check that Terraform files are properly formatted.

    Configuration:
        recursive: bool = True
        check_only: bool = True
    """

    name = "check_format"
    hook_type = HookType.PRE_PLAN
```

#### `terraformik.hooks.validators.variables`

```python
class VariableValidationHook(Hook):
    """
    Validate that required variables are set.

    Configuration:
        required: list[str] = []
        patterns: dict[str, str] = {}
    """

    name = "validate_variables"
    hook_type = HookType.PRE_PLAN
```

#### `terraformik.hooks.validators.security`

```python
class SecurityScanHook(Hook):
    """
    Run security scanning on Terraform code.

    Configuration:
        scanner: str = "tfsec"
        severity_threshold: str = "medium"
        fail_on_warnings: bool = False
    """

    name = "security_scan"
    hook_type = HookType.PRE_APPLY
```

#### `terraformik.hooks.validators.backend`

```python
class BackendValidationHook(Hook):
    """
    Validate backend configuration and resources.

    Configuration:
        check_s3_bucket: bool = True
        check_dynamodb_table: bool = True
        check_permissions: bool = True
    """

    name = "validate_backend"
    hook_type = HookType.PRE_INIT
```

---

## Config Module

### `terraformik.config.loader`

Configuration loading and management.

#### `ConfigLoader`

```python
class ConfigLoader:
    """
    Load and manage tfk configuration.
    """

    DEFAULT_CONFIG_FILES = [
        "tfk.yaml",
        "tfk.yml",
        "tfk.json",
        ".tfk/config.yaml"
    ]

    @classmethod
    def load(
        cls,
        path: Path | str | None = None,
        env_prefix: str = "TFK_"
    ) -> TfkConfig:
        """
        Load configuration from file and environment.

        Args:
            path: Config file path (auto-detected if None)
            env_prefix: Environment variable prefix

        Returns:
            Loaded TfkConfig
        """

    @classmethod
    def create_default(
        cls,
        path: Path | str = "tfk.yaml",
        template: str = "default"
    ) -> TfkConfig:
        """
        Create default configuration file.

        Args:
            path: Output path
            template: Template name

        Returns:
            Created TfkConfig
        """
```

#### `TfkConfig`

```python
@dataclass
class TfkConfig:
    """
    tfk configuration model.

    Attributes:
        version: Config schema version
        terraform: Terraform settings
        backend: Backend configuration
        cloud: Terraform Cloud settings
        workspaces: Workspace configuration
        orchestration: Multi-workspace settings
        hooks: Hook configuration
        output: Output settings
    """

    version: str = "1"
    terraform: TerraformConfig = field(default_factory=TerraformConfig)
    backend: BackendConfig | None = None
    cloud: CloudConfig | None = None
    workspaces: WorkspacesConfig | None = None
    orchestration: OrchestrationConfig | None = None
    hooks: HookConfig = field(default_factory=HookConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def get_var_file(self, environment: str) -> Path | None:
        """Get variable file for environment."""

    def get_workspace_config(self, name: str) -> WorkspaceConfig | None:
        """Get workspace configuration."""
```

---

## Provisioners Module

### `terraformik.provisioners.aws`

AWS backend provisioner.

#### `AWSProvisioner`

```python
class AWSProvisioner(BaseProvisioner):
    """
    Provision AWS backend resources for Terraform state.

    Creates:
        - S3 bucket with versioning and encryption
        - DynamoDB table for state locking
    """

    def __init__(
        self,
        app_name: str,
        environment: str,
        region: str = "us-east-1",
        session: boto3.Session | None = None
    ) -> None:
        """
        Initialize AWS provisioner.

        Args:
            app_name: Application name
            environment: Environment (dev, staging, prod)
            region: AWS region
            session: Boto3 session (optional)
        """
```

##### `provision()`

```python
def provision(self) -> ProvisionResult:
    """
    Provision backend resources.

    Returns:
        ProvisionResult with created resources

    Raises:
        ProvisionerError: If provisioning fails

    Example:
        >>> provisioner = AWSProvisioner(
        ...     app_name="myapp",
        ...     environment="dev",
        ...     region="us-east-1"
        ... )
        >>> result = provisioner.provision()
        >>> print(result.bucket_name)
        myapp-dev-terraformik-state
    """
```

##### `destroy()`

```python
def destroy(self, force: bool = False) -> None:
    """
    Destroy provisioned resources.

    Args:
        force: Force deletion (empty bucket first)

    Raises:
        ProvisionerError: If destruction fails
    """
```

##### `validate()`

```python
def validate(self) -> ValidationResult:
    """
    Validate existing resources.

    Returns:
        ValidationResult with status of each resource
    """
```

---

## HCL Module

### `terraformik.hcl.parser`

HCL parsing utilities.

#### `HCLParser`

```python
class HCLParser:
    """
    Parse HCL/Terraform files.
    """

    @classmethod
    def parse_file(cls, path: Path | str) -> HCLDocument:
        """
        Parse an HCL file.

        Args:
            path: Path to HCL file

        Returns:
            Parsed HCLDocument
        """

    @classmethod
    def parse_string(cls, content: str) -> HCLDocument:
        """
        Parse HCL content string.

        Args:
            content: HCL content

        Returns:
            Parsed HCLDocument
        """
```

#### `HCLDocument`

```python
@dataclass
class HCLDocument:
    """
    Parsed HCL document.

    Attributes:
        blocks: Top-level blocks
        attributes: Top-level attributes
    """

    blocks: list[HCLBlock]
    attributes: dict[str, Any]

    def get_blocks(self, block_type: str) -> list[HCLBlock]:
        """Get all blocks of a type."""

    def get_resources(self) -> list[HCLBlock]:
        """Get all resource blocks."""

    def get_variables(self) -> list[HCLBlock]:
        """Get all variable blocks."""

    def get_outputs(self) -> list[HCLBlock]:
        """Get all output blocks."""
```

### `terraformik.hcl.generator`

HCL generation utilities.

#### `HCLGenerator`

```python
class HCLGenerator:
    """
    Generate HCL content.
    """

    @classmethod
    def generate(cls, document: HCLDocument) -> str:
        """
        Generate HCL string from document.

        Args:
            document: HCL document

        Returns:
            Formatted HCL string
        """

    @classmethod
    def generate_backend(
        cls,
        backend_type: str,
        config: dict[str, Any]
    ) -> str:
        """
        Generate backend configuration block.

        Args:
            backend_type: Backend type (s3, gcs, etc.)
            config: Backend configuration

        Returns:
            HCL backend block
        """
```

---

## Exceptions

### `terraformik.exceptions`

```python
class TerraformikError(Exception):
    """Base exception for all tfk errors."""

    def __init__(
        self,
        message: str,
        details: dict | None = None,
        suggestions: list[str] | None = None
    ):
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []


class ConfigurationError(TerraformikError):
    """Configuration-related errors."""


class InvalidConfigError(ConfigurationError):
    """Invalid configuration value."""


class MissingConfigError(ConfigurationError):
    """Required configuration missing."""


class TerraformError(TerraformikError):
    """Terraform execution errors."""

    def __init__(
        self,
        message: str,
        command: str,
        exit_code: int,
        stdout: str = "",
        stderr: str = "",
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class InitError(TerraformError):
    """Terraform init failed."""


class PlanError(TerraformError):
    """Terraform plan failed."""


class ApplyError(TerraformError):
    """Terraform apply failed."""


class StateError(TerraformError):
    """State-related errors."""


class WorkspaceError(TerraformError):
    """Workspace-related errors."""


class CloudError(TerraformikError):
    """Terraform Cloud API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict | None = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response = response


class AuthenticationError(CloudError):
    """Authentication failed."""


class AuthorizationError(CloudError):
    """Authorization denied."""


class RateLimitError(CloudError):
    """API rate limit exceeded."""


class WorkspaceNotFoundError(CloudError):
    """Workspace not found."""


class RunError(CloudError):
    """Run-related errors."""


class HookError(TerraformikError):
    """Hook execution errors."""


class HookExecutionError(HookError):
    """Hook execution failed."""


class HookTimeoutError(HookError):
    """Hook execution timed out."""


class ProvisionerError(TerraformikError):
    """Backend provisioner errors."""
```

---

## Type Definitions

### `terraformik.types`

```python
from enum import Enum
from typing import TypeVar, Generic
from dataclasses import dataclass


class Command(str, Enum):
    """Terraform commands."""
    INIT = "init"
    PLAN = "plan"
    APPLY = "apply"
    DESTROY = "destroy"
    FMT = "fmt"
    VALIDATE = "validate"
    OUTPUT = "output"


class HookType(str, Enum):
    """Hook execution types."""
    PRE_INIT = "pre_init"
    POST_INIT = "post_init"
    PRE_PLAN = "pre_plan"
    POST_PLAN = "post_plan"
    PRE_APPLY = "pre_apply"
    POST_APPLY = "post_apply"
    PRE_DESTROY = "pre_destroy"
    POST_DESTROY = "post_destroy"


class RunStatus(str, Enum):
    """Terraform Cloud run statuses."""
    PENDING = "pending"
    PLAN_QUEUED = "plan_queued"
    PLANNING = "planning"
    PLANNED = "planned"
    COST_ESTIMATING = "cost_estimating"
    COST_ESTIMATED = "cost_estimated"
    POLICY_CHECKING = "policy_checking"
    POLICY_OVERRIDE = "policy_override"
    POLICY_SOFT_FAILED = "policy_soft_failed"
    POLICY_CHECKED = "policy_checked"
    CONFIRMED = "confirmed"
    APPLY_QUEUED = "apply_queued"
    APPLYING = "applying"
    APPLIED = "applied"
    DISCARDED = "discarded"
    ERRORED = "errored"
    CANCELED = "canceled"
    FORCE_CANCELED = "force_canceled"


class VariableCategory(str, Enum):
    """Variable categories."""
    TERRAFORM = "terraform"
    ENV = "env"


class ExecutionMode(str, Enum):
    """Workspace execution modes."""
    REMOTE = "remote"
    LOCAL = "local"
    AGENT = "agent"


@dataclass
class Changes:
    """Resource change summary."""
    add: int = 0
    change: int = 0
    destroy: int = 0


@dataclass
class PlanResult:
    """Result of terraform plan."""
    success: bool
    changes: Changes
    output: str
    plan_file: Path | None = None


@dataclass
class ApplyResult:
    """Result of terraform apply."""
    success: bool
    changes: Changes
    output: str
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Workspace:
    """Workspace information."""
    id: str
    name: str
    current: bool = False
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class Run:
    """Terraform Cloud run."""
    id: str
    status: RunStatus
    message: str | None = None
    is_destroy: bool = False
    auto_apply: bool = False
    created_at: str | None = None
    plan_only: bool = False


@dataclass
class Variable:
    """Workspace variable."""
    id: str
    key: str
    value: str | None
    category: VariableCategory
    sensitive: bool = False
    hcl: bool = False
    description: str | None = None


T = TypeVar("T")


@dataclass
class PaginatedResponse(Generic[T]):
    """Paginated API response."""
    data: list[T]
    total_count: int
    page_size: int
    page_number: int

    @property
    def has_next(self) -> bool:
        """Check if there are more pages."""
        return self.page_number * self.page_size < self.total_count
```

---

## Usage Examples

### Basic Workflow

```python
from terraformik.core import TerraformExecutor
from terraformik.config import ConfigLoader

# Load configuration
config = ConfigLoader.load()

# Create executor
executor = TerraformExecutor(
    working_dir="./infrastructure",
    env={"TF_VAR_environment": "dev"}
)

# Initialize
init_result = executor.init(
    backend_config=config.backend.config
)

# Plan
plan_result = executor.plan(
    var_file="dev.tfvars",
    out="plan.tfplan"
)

print(f"Changes: {plan_result.changes.add} to add")

# Apply
if plan_result.changes.add > 0:
    apply_result = executor.apply(
        plan_file="plan.tfplan",
        auto_approve=True
    )
    print(f"Applied: {apply_result.changes.add} resources")
```

### Terraform Cloud Integration

```python
from terraformik.cloud import TerraformCloudClient

# Create client
client = TerraformCloudClient(
    token="your-token",
    organization="my-org"
)

# List workspaces
workspaces = client.list_workspaces()
for ws in workspaces.data:
    print(f"{ws.name}: {ws.id}")

# Trigger run
run = client.create_run(
    workspace_id="ws-abc123",
    message="Deploy via tfk",
    auto_apply=False
)

# Wait for plan
run = client.wait_for_run(
    run.id,
    target_statuses=[RunStatus.PLANNED]
)

# Apply
if run.status == RunStatus.PLANNED:
    client.apply_run(run.id, comment="Approved")
```

### Custom Hook

```python
from terraformik.hooks import Hook, HookResult, ExecutionContext, HookType

class TagValidationHook(Hook):
    """Ensure all resources have required tags."""

    name = "validate_tags"
    description = "Validate required tags on resources"
    hook_type = HookType.PRE_APPLY

    def __init__(self, required_tags: list[str]):
        self.required_tags = required_tags

    def execute(self, context: ExecutionContext) -> HookResult:
        plan = context.get_plan()
        if not plan:
            return HookResult(
                success=False,
                message="No plan available"
            )

        missing = []
        for change in plan.resource_changes:
            if change.action in ("create", "update"):
                tags = change.after.get("tags", {})
                for tag in self.required_tags:
                    if tag not in tags:
                        missing.append(f"{change.address}: missing tag '{tag}'")

        if missing:
            return HookResult(
                success=False,
                message=f"Missing required tags:\n" + "\n".join(missing)
            )

        return HookResult(success=True, message="All tags present")


# Register hook
from terraformik.hooks import HookManager

manager = HookManager(config.hooks)
manager.register_hook(TagValidationHook(["Environment", "Owner", "CostCenter"]))
```

---

## See Also

- [User Guide](./user-guide.md)
- [Configuration Reference](./configuration.md)
- [Hooks Reference](./hooks.md)
- [Terraform Cloud Guide](./terraform-cloud.md)
