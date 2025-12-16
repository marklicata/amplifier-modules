# Amplifier Module Registry — Implementation Plan

> **Goal:** Build a Git-backed module registry for discovering, publishing, and installing community and verified modules for `amplifier-foundation`.

---

## Phase 1: Foundation (Schema & Structure)

### 1.1 Define Manifest Schema
Create the `module.yaml` specification that every module must include.

```yaml
# module.yaml schema
name: string              # unique identifier (e.g., "github-issues-agent")
version: string           # semver (e.g., "1.2.0")
description: string       # short description
author: string            # author name or org
license: string           # SPDX identifier (MIT, Apache-2.0, etc.)
repository: string        # optional - source repo URL
homepage: string          # optional - docs/website URL

# Module classification
type: enum                # agent | behavior | bundle | provider | context
tags: list[string]        # searchable tags

# Compatibility
foundation_version: string    # semver range (e.g., ">=0.5.0 <1.0.0")
python_version: string        # e.g., ">=3.10"

# Dependencies
dependencies: list[string]    # other modules (e.g., ["core-http@^1.0.0"])
pip_dependencies: list[string] # Python packages

# Entry points
entry_point: string       # main module path (e.g., "src/agent.py")
exports: list[string]     # what this module exposes

# Source location (one of these)
source:
  type: enum              # "inline" | "git" | "url"
  path: string            # for inline: relative path to source
  repo: string            # for git: repository URL
  ref: string             # for git: branch/tag/commit
  url: string             # for url: tarball download URL

# Metadata
status: enum              # "active" | "deprecated" | "broken"
verified: boolean         # core team verified
created_at: datetime
updated_at: datetime
```

### 1.2 Registry Directory Structure
```
amplifier-modules/
├── README.md                 # Registry overview & contribution guide
├── PLAN.md                   # This file
├── CONTRIBUTING.md           # How to publish modules
├── GOVERNANCE.md             # Verification process, namespace rules
│
├── schema/
│   ├── module.schema.json    # JSON Schema for validation
│   └── validate.py           # Validation script
│
├── registry/
│   ├── index.json            # Master index (auto-generated)
│   │
│   ├── agents/
│   │   └── github-issues-agent/
│   │       ├── module.yaml
│   │       ├── README.md
│   │       ├── CHANGELOG.md
│   │       └── src/          # if inline source
│   │
│   ├── behaviors/
│   ├── bundles/
│   ├── providers/
│   └── context/
│
├── verified/                 # Symlinks or list of verified modules
│   └── verified.json
│
├── analytics/
│   ├── downloads.json        # Download counts per module
│   └── events.jsonl          # Raw telemetry events
│
├── .github/
│   └── workflows/
│       ├── validate-pr.yaml      # Validate module.yaml on PR
│       ├── publish-module.yaml   # Publish on merge
│       ├── update-index.yaml     # Rebuild index.json
│       └── check-broken.yaml     # Scheduled: check foundation compat
│
└── scripts/
    ├── build-index.py        # Generate index.json
    ├── validate-module.py    # Validate a module
    └── check-compat.py       # Check foundation compatibility
```

---

## Phase 2: Validation & Automation

### 2.1 JSON Schema for Validation
Machine-readable schema that GitHub Actions and CLI can use.

### 2.2 GitHub Actions Workflows

**On PR:**
- Validate `module.yaml` against schema
- Check namespace rules (reserved namespaces, collisions)
- Lint source code if inline
- Run module tests if present

**On Merge:**
- Rebuild `index.json`
- Update analytics baseline
- Notify module owner (GitHub issue/comment)

**Scheduled (daily):**
- Check all modules against latest foundation version
- Flag broken modules, update `status: broken`
- Open issues for module owners

### 2.3 Namespace Rules Implementation
```python
RESERVED_NAMESPACES = ["amplifier-", "core-", "microsoft-", "azure-"]

def validate_namespace(module_name: str, is_verified: bool) -> bool:
    for reserved in RESERVED_NAMESPACES:
        if module_name.startswith(reserved) and not is_verified:
            return False
    return True
```

---

## Phase 3: CLI Integration

### 3.1 Commands for `amplifier-foundation`

```bash
# Discovery
amplifier module list                    # List all modules
amplifier module list --type=agent       # Filter by type
amplifier module list --verified         # Only verified
amplifier module search "github"         # Search by name/tags

# Information
amplifier module info <module-name>      # Show module details
amplifier module versions <module-name>  # List versions

# Installation
amplifier module install <module-name>              # Latest version
amplifier module install <module-name>@1.2.0        # Specific version
amplifier module install <module-name> --dev        # Dev dependency

# Management
amplifier module update                  # Update all modules
amplifier module update <module-name>    # Update specific
amplifier module uninstall <module-name> # Remove module
amplifier module outdated                # Show outdated modules

# Publishing (for module authors)
amplifier module init                    # Create module.yaml template
amplifier module validate                # Validate local module
amplifier module publish                 # Submit to registry (opens PR)
```

### 3.2 CLI Implementation Strategy
- Add to `amplifier-foundation` as new subcommand group
- Registry interaction via Git clone/sparse-checkout (no API needed)
- Cache `index.json` locally with TTL
- Install = clone/download + add to project's `modules/` directory

---

## Phase 4: Analytics & Telemetry

### 4.1 Download Tracking
```json
// analytics/downloads.json
{
  "github-issues-agent": {
    "total": 1547,
    "versions": {
      "1.2.0": 892,
      "1.1.0": 655
    },
    "last_30_days": 234
  }
}
```

### 4.2 Event Stream
```jsonl
// analytics/events.jsonl
{"event": "install", "module": "github-issues-agent", "version": "1.2.0", "timestamp": "2025-01-15T10:30:00Z"}
{"event": "search", "query": "github", "results": 5, "timestamp": "2025-01-15T10:31:00Z"}
```

### 4.3 Privacy Considerations
- No PII collected
- Opt-out flag: `amplifier config set telemetry.enabled false`
- Aggregate only in public displays

---

## Phase 5: Breaking Change Detection

### 5.1 Compatibility Checker
```python
# scripts/check-compat.py
async def check_module_compatibility(module: Module, foundation_version: str) -> CompatResult:
    """
    1. Parse module's foundation_version requirement
    2. Check if current foundation satisfies it
    3. Attempt import of module entry_point
    4. Run module's test suite if present
    5. Return pass/fail with details
    """
```

### 5.2 Broken Module Flow
1. Scheduled action detects incompatibility
2. Update `module.yaml`: `status: broken`
3. Add to `broken-modules.json` with details
4. Open GitHub issue mentioning module author
5. CLI shows warning on `amplifier module list`
6. Block installation with `--force` override

---

## Phase 6: Documentation & Governance

### 6.1 CONTRIBUTING.md
- Step-by-step publishing guide
- Module quality guidelines
- Testing requirements
- Review process timeline

### 6.2 GOVERNANCE.md
- Verification criteria and process
- Namespace reservation rules
- Dispute resolution process
- Core team responsibilities

---

## Implementation Order

| #  | Task | Priority | Est. Effort |
|----|------|----------|-------------|
| 1  | Define `module.yaml` schema | Critical | 2 hrs |
| 2  | Create JSON Schema | Critical | 2 hrs |
| 3  | Set up directory structure | Critical | 1 hr |
| 4  | Write validation script | High | 3 hrs |
| 5  | PR validation workflow | High | 2 hrs |
| 6  | Index generation script | High | 2 hrs |
| 7  | CONTRIBUTING.md | High | 2 hrs |
| 8  | GOVERNANCE.md | Medium | 1 hr |
| 9  | CLI: `module list/search/info` | High | 4 hrs |
| 10 | CLI: `module install` | High | 4 hrs |
| 11 | CLI: `module init/validate/publish` | Medium | 4 hrs |
| 12 | Analytics setup | Medium | 3 hrs |
| 13 | Compatibility checker | Medium | 4 hrs |
| 14 | Scheduled broken-check workflow | Medium | 2 hrs |
| 15 | Seed with 2-3 example modules | Low | 2 hrs |

**Total Estimated Effort:** ~38 hours

---

## Future Considerations (README backlog)

- [ ] **Lightweight API layer** — For faster queries than Git cloning
- [ ] **Cryptographic signing** — GPG/Sigstore for verified modules
- [ ] **Module ratings/reviews** — Community feedback system
- [ ] **Dependency resolution** — Handle complex dependency trees
- [ ] **Module bundles** — Curated collections for common use cases

---

## Success Metrics

1. **Adoption:** 10+ community modules within 3 months
2. **Quality:** <5% of modules marked broken at any time
3. **Discovery:** Average search returns relevant results in top 3
4. **Reliability:** 99% of installs succeed without manual intervention
