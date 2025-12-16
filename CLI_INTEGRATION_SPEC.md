# CLI Integration Specification for amplifier-app-cli

**Document Version**: 1.0.0
**Target Repository**: microsoft/amplifier-app-cli
**Last Updated**: 2025-12-16

---

## Executive Summary

This document specifies the complete integration of module registry functionality into the amplifier-app-cli tool. The integration will enable users to discover, search, install, update, and publish modules from the amplifier-modules registry without leaving their terminal.

**Key Features**:
- Module discovery and search
- Seamless installation from git repositories
- Version management and updates
- Publishing workflow for authors
- Dependency resolution (future: phase 2)

---

## Table of Contents

1. [Command Structure](#command-structure)
2. [Registry Client Architecture](#registry-client-architecture)
3. [Installation Mechanism](#installation-mechanism)
4. [Configuration](#configuration)
5. [Command Specifications](#command-specifications)
6. [Error Handling](#error-handling)
7. [Caching Strategy](#caching-strategy)
8. [Security Considerations](#security-considerations)
9. [Testing Requirements](#testing-requirements)
10. [Implementation Phases](#implementation-phases)

---

## Command Structure

### Command Hierarchy

```
amplifier module
├── list [options]              # List/filter available modules
├── search <query> [options]    # Search modules by name/tags/description
├── info <name> [options]       # Show detailed module information
├── install <name>[@version]    # Install a module
├── update [name]               # Update module(s)
├── uninstall <name>            # Remove a module
├── outdated                    # Show outdated modules
├── init                        # Create module.yaml template (for authors)
├── validate [path]             # Validate module manifest (for authors)
└── publish [path]              # Submit module to registry (for authors)
```

### Alias Support

For convenience, provide short aliases:
- `amplifier mod` → `amplifier module`
- `amplifier module i` → `amplifier module install`
- `amplifier module rm` → `amplifier module uninstall`

---

## Registry Client Architecture

### Core Components

```
amplifier-app-cli/
└── src/
    └── modules/
        ├── __init__.py
        ├── registry_client.py      # Fetches and caches registry index
        ├── installer.py             # Handles module installation
        ├── resolver.py              # Version matching and resolution
        ├── cache.py                 # Local cache management
        ├── config.py                # Module configuration
        └── commands/
            ├── list.py
            ├── search.py
            ├── info.py
            ├── install.py
            ├── update.py
            ├── uninstall.py
            ├── outdated.py
            ├── init.py
            ├── validate.py
            └── publish.py
```

### RegistryClient Class

**Purpose**: Fetch, cache, and query the module registry.

**Key Methods**:

```python
class RegistryClient:
    def __init__(self, registry_url: str, cache_dir: Path):
        """Initialize client with registry URL and cache directory."""

    def fetch_index(self, force_refresh: bool = False) -> Dict:
        """
        Fetch registry index.json.
        Uses cache if available and not expired (default TTL: 1 hour).
        """

    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        Search modules by name, tags, description.
        Filters: type, verified, status, tags
        """

    def get_module(self, name: str) -> Optional[Dict]:
        """Get module details by name."""

    def get_manifest(self, name: str, version: str = None) -> Dict:
        """
        Fetch full manifest for specific module version.
        Downloads from git repository if needed.
        """

    def list_modules(self, filters: Dict = None) -> List[Dict]:
        """List all modules with optional filters."""
```

**Implementation Notes**:
- Use `requests` or `httpx` for HTTP fetches
- Cache index.json locally with timestamp
- Support custom registry URL via config/env var
- Validate index schema after fetching

### ModuleInstaller Class

**Purpose**: Install modules from git repositories or embedded source.

**Key Methods**:

```python
class ModuleInstaller:
    def __init__(self, project_dir: Path, modules_dir: Path):
        """
        Initialize installer.
        project_dir: Root of amplifier project
        modules_dir: Where to install modules (default: project_dir/modules)
        """

    def install(
        self,
        module_name: str,
        version: str = None,
        manifest: Dict = None
    ) -> InstallResult:
        """
        Install a module.
        1. Resolve version if not specified
        2. Clone git repository or extract embedded source
        3. Install Python dependencies
        4. Update lockfile
        5. Verify installation
        """

    def uninstall(self, module_name: str) -> bool:
        """Remove module and clean up."""

    def is_installed(self, module_name: str) -> bool:
        """Check if module is installed."""

    def get_installed_version(self, module_name: str) -> Optional[str]:
        """Get currently installed version."""

    def verify_installation(self, module_name: str) -> VerifyResult:
        """
        Verify module installation.
        - Check entry point is importable
        - Verify manifest matches installed code
        - Check dependencies
        """
```

**Installation Process**:

```
install(module_name, version)
  ↓
1. Fetch module manifest from registry
  ↓
2. Resolve version (if not specified, use latest)
  ↓
3. Check if already installed at that version → exit if yes
  ↓
4. Determine installation method (git vs embedded)
  ↓
5a. Git Repository:
    - Clone to temp directory
    - Checkout specific version/tag
    - Copy to modules/ directory
    - Clean up .git directory (optional)
  ↓
5b. Embedded Source:
    - Download source from registry
    - Extract to modules/ directory
  ↓
6. Install Python dependencies (pip install -r requirements.txt if present)
  ↓
7. Update modules.lock file
  ↓
8. Verify installation (try importing entry point)
  ↓
9. Return success/failure
```

### VersionResolver Class

**Purpose**: Match version constraints and resolve compatible versions.

**Key Methods**:

```python
class VersionResolver:
    def resolve_version(
        self,
        module_name: str,
        constraint: Optional[str],
        available_versions: List[str]
    ) -> str:
        """
        Resolve best matching version.
        constraint examples: None, "1.0.0", ">=1.0.0", "^1.2.0"
        """

    def is_compatible(self, version: str, constraint: str) -> bool:
        """Check if version satisfies constraint."""

    def find_latest_compatible(
        self,
        constraint: str,
        versions: List[str]
    ) -> Optional[str]:
        """Find latest version matching constraint."""
```

**Implementation**: Use `packaging.specifiers` for semver matching

---

## Installation Mechanism

### Project Directory Structure

When modules are installed, create this structure:

```
my-amplifier-project/
├── amplifier.yaml              # Project config
├── modules/                    # Installed modules
│   ├── module-one/
│   │   ├── __init__.py
│   │   ├── manifest.yaml       # Copy of manifest
│   │   └── ...                 # Module source
│   └── module-two/
│       └── ...
├── modules.lock                # Lockfile (installed versions)
└── .amplifier/
    └── cache/                  # Local cache
```

### modules.lock Format

**Purpose**: Track installed modules and their versions (like package-lock.json)

```yaml
# modules.lock
version: "1.0"
updated_at: "2025-12-16T10:30:00Z"

modules:
  code-reviewer:
    version: "1.0.0"
    resolved_from: "registry"
    repository:
      url: "https://github.com/microsoft/amplifier-code-reviewer"
      type: "git"
      ref: "v1.0.0"
    installed_at: "2025-12-15T09:00:00Z"
    integrity: "sha256-abc123..."  # Hash of installed code
    dependencies:
      python:
        - "astroid>=3.0.0"
        - "pylint>=3.0.0"

  approval-gate:
    version: "0.5.0"
    resolved_from: "registry"
    repository:
      url: "https://github.com/devtools/amplifier-approval-gate"
      type: "git"
      ref: "v0.5.0"
    installed_at: "2025-12-15T10:15:00Z"
    integrity: "sha256-def456..."
```

### Git Installation Details

**Cloning**:
```python
def install_from_git(repo_url: str, version: str, target_dir: Path):
    """
    Install module from git repository.

    Process:
    1. Clone to temp directory: git clone --depth 1 --branch v{version} {repo_url} temp/
    2. If --branch fails, clone full repo and checkout tag/commit
    3. Copy source to target (excluding .git, tests/, docs/)
    4. Remove temp directory
    """
    temp_dir = tempfile.mkdtemp()

    try:
        # Try shallow clone with specific tag
        subprocess.run([
            "git", "clone",
            "--depth", "1",
            "--branch", f"v{version}",  # Try with 'v' prefix
            repo_url,
            temp_dir
        ], check=True)
    except subprocess.CalledProcessError:
        # Fallback: full clone and checkout
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        subprocess.run([
            "git", "-C", temp_dir,
            "checkout", f"v{version}"  # or try without 'v'
        ], check=True)

    # Copy relevant files
    copy_module_files(temp_dir, target_dir)

    # Cleanup
    shutil.rmtree(temp_dir)
```

**Files to Include/Exclude**:

Include:
- All `.py` files
- `manifest.yaml`
- `README.md`
- `requirements.txt` (if present)
- Any files specified in manifest `include` field

Exclude:
- `.git/`
- `tests/` (unless user specifies --include-tests)
- `.github/`
- `docs/`
- `*.pyc`, `__pycache__/`
- `.pytest_cache/`, `.coverage`

### Python Dependency Installation

After installing module, check for dependencies:

```python
def install_dependencies(module_dir: Path):
    """
    Install Python dependencies for module.

    1. Check for requirements.txt
    2. Check manifest.yaml dependencies.python
    3. Install using pip (into project venv if exists, else user site-packages)
    """
    requirements_file = module_dir / "requirements.txt"
    manifest = load_manifest(module_dir / "manifest.yaml")

    deps_to_install = []

    # From requirements.txt
    if requirements_file.exists():
        deps_to_install.extend(
            requirements_file.read_text().strip().split("\n")
        )

    # From manifest
    if "dependencies" in manifest and "python" in manifest["dependencies"]:
        deps_to_install.extend(manifest["dependencies"]["python"])

    if deps_to_install:
        # Check if in venv
        venv_pip = Path(sys.prefix) / "bin" / "pip"
        pip_cmd = str(venv_pip) if venv_pip.exists() else "pip"

        subprocess.run([
            pip_cmd, "install", *deps_to_install
        ], check=True)
```

---

## Configuration

### Registry Configuration

Users can configure registry settings via:

1. **Environment Variable** (highest precedence):
   ```bash
   export AMPLIFIER_REGISTRY_URL="https://custom-registry.example.com"
   ```

2. **amplifier.yaml** (project-level):
   ```yaml
   modules:
     registry: "https://custom-registry.example.com"
     modules_dir: "./modules"  # Custom modules directory
     cache_ttl: 3600  # Cache TTL in seconds
   ```

3. **~/.amplifierrc** (user-level):
   ```yaml
   modules:
     registry: "https://github.com/microsoft/amplifier-modules/raw/main/registry"
     install_dev_dependencies: false
   ```

4. **Default**:
   ```
   https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json
   ```

### ModuleConfig Class

```python
class ModuleConfig:
    @classmethod
    def load(cls) -> "ModuleConfig":
        """
        Load configuration from all sources, with precedence.
        Returns merged configuration.
        """

    @property
    def registry_url(self) -> str:
        """Get registry URL (with precedence resolution)."""

    @property
    def modules_dir(self) -> Path:
        """Get modules installation directory."""

    @property
    def cache_dir(self) -> Path:
        """Get cache directory (~/.amplifier/cache by default)."""

    @property
    def cache_ttl(self) -> int:
        """Get cache TTL in seconds (default: 3600)."""
```

---

## Command Specifications

### 1. amplifier module list

**Purpose**: List available modules with filtering

**Usage**:
```bash
amplifier module list [options]
```

**Options**:
```
--type <type>        Filter by module type (agent, behavior, provider, bundle, context)
--verified           Show only verified modules
--community          Show only community modules
--status <status>    Filter by status (active, deprecated, broken, archived)
--tag <tag>          Filter by tag
--json               Output as JSON
--compact            Compact output (names only)
```

**Example Output**:
```
Available Modules (3)
════════════════════════════════════════════════════════════════

✓ code-reviewer (1.0.0) [agent]
  Automated code review agent
  Tags: code-quality, automation, review
  Author: Amplifier Team (microsoft)

  approval-gate (0.5.0) [behavior]
  Human approval gates for workflows
  Tags: workflow, approval, human-in-the-loop
  Author: DevToolsContributor (devtoolscontributor)

✓ hello-world (1.0.0) [agent]
  Minimal embedded example agent
  Tags: example, tutorial
  Author: Amplifier Team (microsoft)

Legend: ✓ = Verified
```

**JSON Output**:
```json
{
  "total": 3,
  "modules": [
    {
      "name": "code-reviewer",
      "version": "1.0.0",
      "type": "agent",
      "verified": true,
      "description": "Automated code review agent",
      "author": "Amplifier Team",
      "author_github": "microsoft"
    }
  ]
}
```

### 2. amplifier module search

**Purpose**: Search modules by keyword

**Usage**:
```bash
amplifier module search <query> [options]
```

**Search Fields**:
- Module name
- Description
- Tags
- Keywords
- Author

**Options**: Same as `list`, plus:
```
--limit <n>    Max results (default: 10)
```

**Example**:
```bash
$ amplifier module search "code review"

Found 2 modules matching "code review":

✓ code-reviewer (1.0.0)
  Automated code review agent
  Relevance: ████████░░ 80%

  review-assistant (0.3.0)
  AI-powered review assistant
  Relevance: ██████░░░░ 60%
```

**Search Algorithm**:
- Exact name match: 100% relevance
- Name contains query: 80%
- Description contains query: 60%
- Tags contain query: 70%
- Keywords contain query: 50%
- Sort by relevance descending

### 3. amplifier module info

**Purpose**: Show detailed information about a module

**Usage**:
```bash
amplifier module info <name> [options]
```

**Options**:
```
--version <version>    Show specific version (default: latest)
--json                 Output as JSON
```

**Example Output**:
```
code-reviewer (1.0.0) ✓ Verified
═══════════════════════════════════════════════════════════════

Description:
  Automated code review agent that analyzes code quality, style,
  and potential issues

Author: Amplifier Team (microsoft)
License: MIT
Homepage: https://github.com/microsoft/amplifier-code-reviewer

Type: agent
Entry Point: code_reviewer.agent:CodeReviewerAgent
Status: active

Compatibility:
  Foundation: >=0.1.0
  Python: >=3.10

Dependencies:
  Python Packages:
    - astroid>=3.0.0
    - pylint>=3.0.0

Capabilities:
  - code-analysis
  - style-checking
  - best-practices

Tags: code-quality, automation, review, linting

Versions:
  1.0.0 (latest)

Installation:
  amplifier module install code-reviewer
```

### 4. amplifier module install

**Purpose**: Install a module

**Usage**:
```bash
amplifier module install <name>[@version] [options]
```

**Options**:
```
--save-dev             Mark as dev dependency
--no-deps              Skip Python dependency installation
--force                Reinstall even if already installed
--dry-run              Show what would be installed
```

**Examples**:
```bash
# Install latest version
amplifier module install code-reviewer

# Install specific version
amplifier module install code-reviewer@1.0.0

# Install as dev dependency
amplifier module install hello-world --save-dev
```

**Output**:
```
Installing code-reviewer@1.0.0...

✓ Fetching manifest from registry
✓ Cloning repository (https://github.com/microsoft/amplifier-code-reviewer)
✓ Installing to modules/code-reviewer/
✓ Installing Python dependencies (2 packages)
✓ Verifying installation
✓ Updating modules.lock

Successfully installed code-reviewer@1.0.0
```

**Error Cases**:
- Module not found → Show similar names
- Version not found → Show available versions
- Already installed → Show `--force` option
- Git clone fails → Show repository URL, suggest checking access
- Dependency install fails → Show failed packages, suggest manual install

### 5. amplifier module update

**Purpose**: Update module(s) to latest compatible version

**Usage**:
```bash
amplifier module update [name] [options]
```

**Options**:
```
--all         Update all modules
--dry-run     Show what would be updated
--patch       Only update patch versions
--minor       Only update minor versions
```

**Examples**:
```bash
# Update specific module
amplifier module update code-reviewer

# Update all modules
amplifier module update --all

# Show what would be updated
amplifier module update --all --dry-run
```

**Output**:
```
Checking for updates...

code-reviewer: 1.0.0 → 1.2.0 (latest)
approval-gate: 0.5.0 (already latest)

Update 1 module? [Y/n] y

Updating code-reviewer to 1.2.0...
✓ Downloaded and installed

Updated 1 module
```

### 6. amplifier module uninstall

**Purpose**: Remove an installed module

**Usage**:
```bash
amplifier module uninstall <name> [options]
```

**Options**:
```
--keep-deps    Keep Python dependencies
--force        Skip confirmation
```

**Output**:
```
Uninstalling code-reviewer...

This will remove:
  - modules/code-reviewer/
  - Python dependencies (astroid, pylint)

Continue? [y/N] y

✓ Removed module files
✓ Uninstalled Python dependencies
✓ Updated modules.lock

Successfully uninstalled code-reviewer
```

### 7. amplifier module outdated

**Purpose**: Show modules with available updates

**Usage**:
```bash
amplifier module outdated [options]
```

**Options**:
```
--json    Output as JSON
```

**Output**:
```
Checking installed modules...

Module            Current    Latest    Type
───────────────────────────────────────────
code-reviewer     1.0.0      1.2.0     minor
approval-gate     0.4.0      0.5.0     minor

2 modules can be updated
Run: amplifier module update --all
```

### 8. amplifier module init

**Purpose**: Create a module manifest template (for module authors)

**Usage**:
```bash
amplifier module init [options]
```

**Options**:
```
--name <name>          Module name
--type <type>          Module type
--interactive          Interactive prompt (default)
--output <file>        Output file (default: manifest.yaml)
```

**Interactive Mode**:
```
Creating new Amplifier module...

Module name: my-awesome-agent
Module type:
  1. agent
  2. behavior
  3. provider
  4. bundle
  5. context
Choose [1-5]: 1

Description: A custom agent for my use case
Author name: Your Name
Author email: you@example.com
Author GitHub username: yourusername

Repository URL (optional): https://github.com/yourusername/my-awesome-agent
License [MIT]:

✓ Created manifest.yaml

Next steps:
  1. Edit manifest.yaml to add more details
  2. Implement your module
  3. Run: amplifier module validate
  4. Run: amplifier module publish
```

### 9. amplifier module validate

**Purpose**: Validate module manifest (for module authors)

**Usage**:
```bash
amplifier module validate [path] [options]
```

**Options**:
```
--strict      Treat warnings as errors
--fix         Auto-fix issues where possible
```

**Example**:
```bash
$ amplifier module validate ./manifest.yaml

Validating manifest.yaml...

✓ Schema validation passed
✓ Entry point format valid
✓ Version constraint valid
⚠ Missing GitHub username (recommended)
⚠ Description is short (20 chars, recommend >50)

Validation passed with 2 warnings
```

### 10. amplifier module publish

**Purpose**: Submit module to registry (opens PR)

**Usage**:
```bash
amplifier module publish [path] [options]
```

**Options**:
```
--manifest <file>    Path to manifest.yaml (default: ./manifest.yaml)
--fork               Fork registry automatically
--draft              Create draft PR
```

**Process**:
1. Validate manifest locally
2. Check if user has forked amplifier-modules
3. If not, prompt to fork (or create fork via API)
4. Clone fork
5. Add module to registry/modules/[name]/
6. Commit changes
7. Push to fork
8. Open PR via GitHub API

**Output**:
```
Publishing my-awesome-agent...

✓ Manifest validation passed
✓ Checking registry fork
→ Forking microsoft/amplifier-modules to yourusername/amplifier-modules
✓ Cloning fork
✓ Adding module to registry/modules/my-awesome-agent/
✓ Committing changes
✓ Pushing to fork
✓ Creating pull request

Pull request created: https://github.com/microsoft/amplifier-modules/pull/42

Your module will be reviewed by the registry team.
You'll receive notifications when there are updates.
```

---

## Error Handling

### Error Categories

1. **Network Errors**
   - Registry unreachable
   - Git clone fails
   - Timeout

2. **Validation Errors**
   - Invalid manifest
   - Missing required fields
   - Version constraint malformed

3. **Installation Errors**
   - Module not found
   - Version not available
   - Git repository access denied
   - Disk space insufficient
   - Dependency installation fails

4. **Conflict Errors**
   - Module already installed (different version)
   - Namespace collision
   - Dependency conflicts

### Error Messages

**Good Error Message Pattern**:
```
ERROR: Failed to install code-reviewer

Reason: Git repository not accessible
  Repository: https://github.com/microsoft/amplifier-code-reviewer
  Error: Permission denied (publickey)

Possible solutions:
  1. Check your SSH key is configured: https://docs.github.com/authentication
  2. Try using HTTPS URL instead of SSH
  3. Verify repository exists and is public

Need help? https://docs.amplifier.dev/troubleshooting
```

### Retry Logic

For network operations:
- **Registry fetch**: 3 retries with exponential backoff
- **Git clone**: 2 retries
- **Dependency install**: 1 retry

---

## Caching Strategy

### Index Caching

**Cache Location**: `~/.amplifier/cache/registry-index.json`

**Cache Entry**:
```json
{
  "url": "https://...",
  "fetched_at": "2025-12-16T10:00:00Z",
  "ttl": 3600,
  "data": { ...index contents... }
}
```

**TTL (Time To Live)**: 1 hour (configurable)

**Invalidation**:
- Manual: `amplifier module list --refresh`
- Automatic: After TTL expires
- On error: Falls back to cached version with warning

### Manifest Caching

**Cache Location**: `~/.amplifier/cache/manifests/[module-name]/[version].yaml`

**Purpose**: Avoid re-fetching manifests for specific versions

**TTL**: 24 hours (manifests rarely change for published versions)

---

## Security Considerations

### 1. Repository Trust

**Problem**: Users may install modules from untrusted repositories

**Mitigations**:
- Show verified badge prominently
- Warn when installing unverified modules
- Display author and repository URL before installation
- Require confirmation for unverified modules

**Example**:
```
⚠ Warning: Installing unverified community module

Module: some-module (by unknown-author)
Repository: https://github.com/unknown-author/some-module

This module is not verified by the Amplifier team.
Review the source code before installing.

Continue? [y/N]
```

### 2. Code Execution

**Problem**: Modules contain Python code that will be executed

**Mitigations**:
- Sandbox option (future enhancement)
- Clear warnings about code execution
- Show module capabilities/permissions (if defined in manifest)
- Allow dry-run to inspect what will be installed

### 3. Dependency Integrity

**Problem**: Dependencies may have vulnerabilities

**Mitigations**:
- Show all dependencies before installation
- Integrate with `pip audit` or `safety` to check for CVEs
- Store integrity hashes in modules.lock
- Warn about dependencies with known vulnerabilities

### 4. Registry Integrity

**Problem**: Registry could be compromised

**Mitigations**:
- Use HTTPS for registry communication
- Verify index.json schema
- Future: GPG signing of registry index
- Future: Module signing by authors

---

## Testing Requirements

### Unit Tests

1. **RegistryClient**:
   - Test fetch with mocked HTTP responses
   - Test caching behavior
   - Test error handling (network errors, invalid JSON)
   - Test search and filter logic

2. **ModuleInstaller**:
   - Test git cloning (with mocked git commands)
   - Test file copying and exclusions
   - Test dependency installation
   - Test lockfile updates
   - Test rollback on failure

3. **VersionResolver**:
   - Test semver matching
   - Test latest version selection
   - Test constraint parsing

### Integration Tests

1. **End-to-End Installation**:
   - Create test registry
   - Install module from test registry
   - Verify files are in place
   - Verify entry point is importable
   - Uninstall and verify cleanup

2. **Update Flow**:
   - Install old version
   - Update to new version
   - Verify upgrade succeeded

3. **Dependency Resolution** (Phase 2):
   - Install module with dependencies
   - Verify all dependencies installed

### Manual Testing Checklist

- [ ] Install verified module
- [ ] Install community module with warning
- [ ] Install specific version
- [ ] Update to latest version
- [ ] Uninstall module
- [ ] Search and list modules
- [ ] Validate and publish workflow
- [ ] Error handling (network down, git fails, etc.)
- [ ] Cache expiration and refresh

---

## Implementation Phases

### Phase 1: Core Functionality (MVP)

**Goal**: Basic install, list, search commands working

**Tasks**:
1. Implement RegistryClient (fetch, cache, search)
2. Implement ModuleInstaller (git clone, file copy)
3. Implement `list`, `search`, `info` commands
4. Implement `install` command (git repositories only)
5. Implement `uninstall` command
6. Basic error handling
7. Unit tests for core classes

**Timeline**: 2-3 weeks

**Success Criteria**:
- Users can list modules from registry
- Users can install modules from git repos
- Files are correctly placed in modules/ directory
- Basic caching works

### Phase 2: Enhancements

**Goal**: Version management, updates, better UX

**Tasks**:
1. Implement VersionResolver
2. Implement `update` and `outdated` commands
3. Add modules.lock file
4. Improve error messages and help text
5. Add progress indicators
6. Integration tests

**Timeline**: 2 weeks

**Success Criteria**:
- Version constraints work correctly
- Update flow is smooth
- Lockfile tracks installed versions

### Phase 3: Author Tools

**Goal**: Support module authors

**Tasks**:
1. Implement `init` command
2. Implement `validate` command
3. Implement `publish` command (GitHub PR workflow)
4. Add interactive prompts
5. Documentation for module authors

**Timeline**: 1-2 weeks

**Success Criteria**:
- Authors can scaffold new modules
- Validation catches common errors
- Publishing flow creates correct PRs

### Phase 4: Advanced Features

**Goal**: Dependency resolution, security

**Tasks**:
1. Simple dependency resolution (Phase 1 approach)
2. Integrate security scanning (pip audit)
3. Support embedded modules
4. Better caching strategies
5. Offline mode

**Timeline**: 2-3 weeks

**Success Criteria**:
- Dependencies are auto-installed
- Security warnings shown
- Works with limited connectivity

---

## Appendix: Example Code Snippets

### Fetching Registry Index

```python
import requests
from pathlib import Path
import json
from datetime import datetime, timedelta

class RegistryClient:
    def __init__(self, registry_url: str, cache_dir: Path):
        self.registry_url = registry_url
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "registry-index.json"
        self.cache_ttl = 3600  # 1 hour

    def fetch_index(self, force_refresh: bool = False) -> dict:
        """Fetch registry index with caching."""
        if not force_refresh and self.cache_file.exists():
            cache_data = json.loads(self.cache_file.read_text())
            fetched_at = datetime.fromisoformat(cache_data["fetched_at"])
            age = (datetime.now() - fetched_at).total_seconds()

            if age < self.cache_ttl:
                return cache_data["data"]

        # Fetch from registry
        response = requests.get(self.registry_url, timeout=10)
        response.raise_for_status()
        index_data = response.json()

        # Cache it
        cache_data = {
            "url": self.registry_url,
            "fetched_at": datetime.now().isoformat(),
            "ttl": self.cache_ttl,
            "data": index_data
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(cache_data, indent=2))

        return index_data

    def search(self, query: str) -> list[dict]:
        """Search modules."""
        index = self.fetch_index()
        results = []

        for name, module in index["modules"].items():
            relevance = 0

            # Exact name match
            if name.lower() == query.lower():
                relevance = 100
            elif query.lower() in name.lower():
                relevance = 80
            elif query.lower() in module.get("description", "").lower():
                relevance = 60
            elif any(query.lower() in tag.lower() for tag in module.get("tags", [])):
                relevance = 70

            if relevance > 0:
                results.append({
                    "name": name,
                    **module,
                    "relevance": relevance
                })

        return sorted(results, key=lambda x: x["relevance"], reverse=True)
```

### Installing Module from Git

```python
import subprocess
import tempfile
import shutil
from pathlib import Path

class ModuleInstaller:
    def install_from_git(
        self,
        module_name: str,
        repo_url: str,
        version: str,
        target_dir: Path
    ):
        """Install module from git repository."""
        temp_dir = Path(tempfile.mkdtemp())

        try:
            # Try shallow clone with tag
            tag = f"v{version}"
            try:
                subprocess.run([
                    "git", "clone",
                    "--depth", "1",
                    "--branch", tag,
                    repo_url,
                    str(temp_dir)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # Fallback: full clone and checkout
                subprocess.run([
                    "git", "clone", repo_url, str(temp_dir)
                ], check=True, capture_output=True)

                subprocess.run([
                    "git", "-C", str(temp_dir),
                    "checkout", tag
                ], check=True, capture_output=True)

            # Copy files to target
            self._copy_module_files(temp_dir, target_dir)

        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _copy_module_files(self, source: Path, target: Path):
        """Copy module files, excluding git and test files."""
        exclude_patterns = [
            ".git", ".github", "tests", "__pycache__",
            "*.pyc", ".pytest_cache", ".coverage", "docs"
        ]

        target.mkdir(parents=True, exist_ok=True)

        for item in source.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(source)

                # Check exclusions
                if any(pattern in str(rel_path) for pattern in exclude_patterns):
                    continue

                dest = target / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
```

---

## References

- Registry Repository: https://github.com/microsoft/amplifier-modules
- Registry Index: https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json
- Module Manifest Schema: https://github.com/microsoft/amplifier-modules/blob/main/schemas/module-manifest.schema.json

---

**End of Specification**

This document should be shared with the amplifier-app-cli team for implementation planning and review.
