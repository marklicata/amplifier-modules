# CLI Integration Specification for amplifier-app-cli

**Document Version**: 2.0.0 (Minimal - Discovery Only)
**Target Repository**: microsoft/amplifier-app-cli
**Last Updated**: 2025-12-16

---

## Executive Summary

This document specifies a minimal integration of the amplifier-modules registry into the amplifier-app-cli tool for **discovery purposes only**. The amplifier-modules repository provides a registry of available modules. The CLI integration adds discovery commands to help users find modules, then delegates to Amplifier's existing module management functionality.

**Key Principle**:
- amplifier-modules = Registry (discovery layer)
- amplifier-app-cli = Already has module management
- This spec = Bridge between them for discovery

**What This Adds**:
- Read from the amplifier-modules registry
- Module discovery commands (list, search, info)
- Integration with existing `amplifier source add` and `amplifier module add` commands

**What Amplifier Already Handles**:
- Module installation
- Module management
- Git cloning and file operations
- Dependency management

---

## Table of Contents

1. [Command Structure](#command-structure)
2. [Registry Client](#registry-client)
3. [Command Specifications](#command-specifications)
4. [Implementation Plan](#implementation-plan)

---

## Command Structure

### Using Existing Amplifier Commands

Amplifier CLI already has commands for adding sources and modules. We're just adding discovery functionality on top:

**Step 1: Registry Source (should be included by default)**

The amplifier-modules registry should be configured as a default source in Amplifier so users don't need to manually add it. The Amplifier team should configure this in their default sources/configuration.

**Registry URL**: `https://github.com/microsoft/amplifier-modules`

*Note: Implementation detail for amplifier-app-cli maintainers to determine the best way to include this as a default source.*

**Step 2: Discover Modules (new - reads from registry)**
```bash
amplifier module list [options]        # List modules in registry
amplifier module search <query>        # Search registry
amplifier module info <name>           # Show module details from registry
```

**Step 3: Add Module (existing command)**
```bash
amplifier module add <name>            # Use existing amplifier module add
```

### What's New vs. What Exists

**New (this spec)**:
- `amplifier module list` - Read and display modules from registry
- `amplifier module search` - Search modules in registry
- `amplifier module info` - Show module details from registry

**Already Exists in Amplifier**:
- `amplifier source add` - Add a source (already works)
- `amplifier module add` - Add/install a module (already works)

The new commands just provide a discovery layer that reads from the amplifier-modules registry.

---

## Registry Client

### Core Components

```
amplifier-app-cli/
└── src/
    └── registry/
        ├── __init__.py
        ├── client.py          # Fetches and caches registry index
        └── commands/
            ├── list.py        # List modules from registry
            ├── search.py      # Search modules in registry
            └── info.py        # Show module details from registry
```

### RegistryClient Class

**Purpose**: Fetch, cache, and query the amplifier-modules registry. Provides discovery only - does NOT handle installation.

**Key Methods**:

```python
class RegistryClient:
    def __init__(self):
        """Initialize with default registry URL and cache location."""
        self.registry_url = "https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json"
        self.cache_dir = Path.home() / ".amplifier" / "cache"
        self.cache_ttl = 3600  # 1 hour

    def fetch_index(self) -> Dict:
        """
        Fetch registry index.json.
        Uses cache if available and not expired.
        """

    def list_modules(self, filters: Dict = None) -> List[Dict]:
        """
        List all modules with optional filters.
        Filters: type, verified
        """

    def search(self, query: str) -> List[Dict]:
        """
        Search modules by name, description, and tags.
        Returns sorted by relevance.
        """

    def get_module(self, name: str) -> Optional[Dict]:
        """Get module details by name."""
```

**Implementation Notes**:
- Simple HTTP fetch using `requests`
- Cache index.json locally (1 hour TTL)
- Read-only - just provides discovery
- Amplifier handles the actual module installation

---

## Command Specifications

### 1. amplifier module list

**Purpose**: List available modules from the registry

**Usage**:
```bash
amplifier module list [options]
```

**Options**:
```
--type <type>        Filter by module type (agent, behavior, provider, bundle, context)
--verified           Show only verified modules
--json               Output as JSON
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

**Options**:
```
--type <type>     Filter by module type
--verified        Show only verified modules
--json            Output as JSON
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

**Search Algorithm** (Simple):
- Exact name match: 100% relevance
- Name contains query: 80%
- Description contains query: 60%
- Tags contain query: 70%
- Sort by relevance descending

### 3. amplifier module info

**Purpose**: Show detailed information about a module

**Usage**:
```bash
amplifier module info <name> [options]
```

**Options**:
```
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
Repository: https://github.com/microsoft/amplifier-code-reviewer

Type: agent
Entry Point: code_reviewer.agent:CodeReviewerAgent

Compatibility:
  Foundation: >=0.1.0
  Python: >=3.10

Tags: code-quality, automation, review, linting

Installation:
  amplifier module add code-reviewer
```

### 4. Using amplifier module add

**Purpose**: After discovering modules, users add them using Amplifier's existing command

**Usage**:
```bash
amplifier module add <name>
```

**Example**:
```bash
# After discovering code-reviewer via list/search
amplifier module add code-reviewer
```

**Note**: This command already exists in Amplifier. The discovery commands above just help users find the right module name to use with this existing command. Amplifier handles:
- Fetching the module
- Installation
- Git operations
- Dependencies


---

## Error Handling

### Error Categories

1. **Registry Fetch Errors**
   - Registry URL unreachable
   - Invalid JSON in registry
   - Cache read/write errors

2. **Discovery Errors**
   - Module not found in registry
   - Invalid search query

### Error Messages

**Good Error Message Pattern**:
```
ERROR: Failed to fetch module registry

Reason: Network connection failed
  URL: https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json

Possible solutions:
  1. Check your internet connection
  2. Try again in a few moments
  3. Using cached registry data (if available)
```

**Module Not Found**:
```
ERROR: Module 'xyz' not found in registry

Did you mean:
  - code-reviewer
  - review-assistant

Run 'amplifier module list' to see all available modules
```

### Retry Logic

For network operations:
- **Registry fetch**: 2 retries with exponential backoff
- **On failure**: Fall back to cached data if available

---

## Implementation Plan

### Single Phase: Discovery Layer

**Goal**: Add module discovery by reading from the amplifier-modules registry

**Tasks**:
1. Implement RegistryClient
   - Fetch index.json from GitHub
   - File-based cache with 1-hour TTL
   - List, search, and get_module functions
   - Error handling with fallback to cache

2. Implement Discovery Commands
   - `amplifier module list` - List modules from registry
   - `amplifier module search <query>` - Search modules
   - `amplifier module info <name>` - Show module details

3. Testing
   - Unit tests for RegistryClient
   - Unit tests for search/filter logic
   - Integration test with real registry
   - Manual testing of all commands

**Success Criteria**:
- Users can list all modules from the registry
- Users can search for modules by keyword
- Users can view detailed info about a module
- Registry index is cached to reduce network calls
- Graceful error handling when registry is unavailable
- Clear integration with existing `amplifier module add` command

**What We're NOT Building**:
- Module installation (Amplifier already does this)
- Git operations (Amplifier handles this)
- Version management (future enhancement)
- Publishing workflow (future enhancement)

This is purely a **discovery layer** that reads from the registry and displays information to users.

---

## Appendix: Example Code

### RegistryClient (Discovery Only)

```python
import requests
from pathlib import Path
import json
from datetime import datetime

class RegistryClient:
    """
    Reads from amplifier-modules registry for module discovery.
    Does NOT handle installation - that's done by Amplifier.
    """

    def __init__(self):
        self.registry_url = "https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json"
        self.cache_dir = Path.home() / ".amplifier" / "cache"
        self.cache_file = self.cache_dir / "registry-index.json"
        self.cache_ttl = 3600  # 1 hour

    def fetch_index(self) -> dict:
        """Fetch registry index with caching."""
        # Check cache
        if self.cache_file.exists():
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
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_data = {
            "fetched_at": datetime.now().isoformat(),
            "data": index_data
        }
        self.cache_file.write_text(json.dumps(cache_data, indent=2))

        return index_data

    def list_modules(self, filters: dict = None) -> list[dict]:
        """List all modules with optional filters."""
        index = self.fetch_index()
        modules = []

        for name, module in index["modules"].items():
            # Apply filters
            if filters:
                if filters.get("type") and module.get("type") != filters["type"]:
                    continue
                if filters.get("verified") and not module.get("verified"):
                    continue

            modules.append({"name": name, **module})

        return modules

    def search(self, query: str) -> list[dict]:
        """Search modules by name, description, and tags."""
        index = self.fetch_index()
        results = []

        for name, module in index["modules"].items():
            relevance = 0

            if name.lower() == query.lower():
                relevance = 100
            elif query.lower() in name.lower():
                relevance = 80
            elif query.lower() in module.get("description", "").lower():
                relevance = 60
            elif any(query.lower() in tag.lower() for tag in module.get("tags", [])):
                relevance = 70

            if relevance > 0:
                results.append({"name": name, **module, "relevance": relevance})

        return sorted(results, key=lambda x: x["relevance"], reverse=True)

    def get_module(self, name: str) -> dict | None:
        """Get details for a specific module."""
        index = self.fetch_index()
        module = index["modules"].get(name)

        if module:
            return {"name": name, **module}
        return None
```

---

## References

- Registry Repository: https://github.com/microsoft/amplifier-modules
- Registry Index: https://raw.githubusercontent.com/microsoft/amplifier-modules/main/registry/index.json
- Module Manifest Schema: https://github.com/microsoft/amplifier-modules/blob/main/schemas/module-manifest.schema.json

---

**End of Specification**

This specification defines a **discovery-only** integration layer. The amplifier-modules repository provides the registry, and this integration adds commands to read and search that registry. All module installation, management, and Git operations are handled by Amplifier's existing functionality.
