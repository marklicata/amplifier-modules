# amplifier-module-registry

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/microsoft/amplifier-module-registry/actions)
[![Modules](https://img.shields.io/badge/modules-23-blue.svg)](./registry)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Official module registry for [amplifier-foundation](https://github.com/microsoft/amplifier-foundation) — Microsoft's Python framework for building modular, agent-driven AI applications.

## 🎯 Why This Exists

Building AI agents shouldn't mean reinventing the wheel. The amplifier ecosystem needs a way for developers to:

- **Discover** → Find pre-built agents, tools, and integrations instead of building from scratch
- **Trust** → Identify verified, quality-checked modules from the community
- **Share** → Publish reusable components that solve common problems
- **Extend** → Build on amplifier-foundation without bloating the core framework

**This registry makes amplifier modular, extensible, and community-driven.**

## 📦 What is this?

This repository is the **central catalog** for amplifier-foundation modules. Think of it like the npm registry website or PyPI's package index — a discoverable directory where:

- **Module authors** publish their work by submitting manifests (metadata files)
- **Module consumers** browse and discover what's available
- **Tools** (like [`amplifier-app-cli`](https://github.com/microsoft/amplifier-app-cli)) read the registry to enable module management

This is a **registry/catalog** where modules are added and removed. Module consumption happens in other tools that read from this registry.

## 🚀 Quick Start

### Browse Modules

Browse the [`registry/`](./registry) directory or check [`registry/index.json`](./registry/index.json) for the complete listing of [verified](.registry/verified/) and [community](.registry/modules/) modules.

### Consuming Modules
Want to use modules from this registry in your amplifier application? See individual amplifier app implementations for details on discovering and integrating modules into your projects. [`amplifier-app-cli`](https://github.com/microsoft/amplifier-app-cli) is one example.

### Publish Your Module

1. **Create your manifest** — Copy [`examples/manifest.example.yaml`](./examples/manifest.example.yaml)
2. **Validate locally** — `python scripts/validate_manifest.py your-manifest.yaml`
3. **Submit a PR** — Add your module to `registry/modules/your-module-name/manifest.yaml`
4. **Automated checks** — CI validates your manifest
5. **Merge & publish** — Your module appears in the index

## 📁 Repository Structure

```
amplifier-module-registry/
├── registry/
│   ├── modules/           # Community modules
│   │   └── module-name/
│   │       ├── manifest.yaml
│   │       └── versions/   # Historical versions (optional)
│   ├── verified/          # Core team verified modules
│   │   └── module-name/
│   │       └── manifest.yaml
│   └── index.json         # Auto-generated registry index
├── schemas/
│   ├── module-manifest.schema.json
│   └── registry-index.schema.json
├── scripts/
│   ├── validate_manifest.py
│   └── generate_index.py
├── examples/
│   ├── manifest.example.yaml
│   └── manifest.minimal.yaml
└── .github/workflows/
    ├── validate-manifest.yml
    └── publish-module.yml
```

## 📋 Module Types

| Type | Description |
|------|-------------|
| `agent` | Autonomous agents with specific capabilities |
| `behavior` | Reusable behavior patterns for agents |
| `provider` | External service integrations (LLMs, APIs, etc.) |
| `bundle` | Pre-configured collections of modules |
| `context` | Context providers and enhancers |

## ✅ Verified vs Community Modules

| | Verified | Community |
|---|----------|-----------|
| **Location** | `registry/verified/` | `registry/modules/` |
| **Review** | Core team approved | Automated validation only |
| **Badge** | ✓ Verified | — |
| **Trust level** | Higher | Standard |

Only the core team can publish to `verified/`. Community modules are first-come-first-served with automated quality checks.

## 🔖 Reserved Namespaces

The following prefixes are reserved for official use:
- `amplifier-*`, `amp-*`
- `microsoft-*`, `msft-*`
- `azure-*`
- `official-*`, `core-*`, `foundation-*`

## 📊 Analytics

Analytics collection is not currently implemented. When added, it will be opt-in with no personally identifiable information collected.

## 🛡️ Governance

Module verification, namespace management, and lifecycle policies are defined in [GOVERNANCE.md](./GOVERNANCE.md).

**Key Points**:
- Verification process: 10-day SLA by Microsoft OCTO MADE team
- Focus on product definition (audience, problem, solution)
- Reserved namespaces for Microsoft/core team
- Breaking change detection runs weekly

## 🛠️ Local Development

```bash
# Clone the registry
git clone https://github.com/microsoft/amplifier-module-registry
cd amplifier-module-registry

# Set up Python environment (in WSL or Linux)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run tests
pytest

# Validate a manifest
python scripts/validate_manifest.py examples/manifest.example.yaml

# Check compatibility with foundation version
python scripts/check_compat.py --foundation-version 0.1.0

# Regenerate the index
python scripts/generate_index.py --pretty
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_validate_manifest.py

# Run with verbose output
pytest -v
```

## 🗺️ Roadmap

### ✅ Completed (v1.0)
- [x] JSON Schema for module manifests
- [x] Validation scripts with comprehensive checks
- [x] GitHub Actions CI/CD (PR validation, publishing, testing)
- [x] Registry structure (modules + verified directories)
- [x] Core module collection (23 modules: orchestrators, tools, hooks, providers, context)
- [x] Testing infrastructure (pytest, fixtures, 80%+ coverage target)
- [x] Governance documentation
- [x] Breaking change detection (weekly automated checks)
- [x] Verification request process
- [x] CLI Integration (https://github.com/microsoft/amplifier-app-cli)

### 🔮 Future
- [ ] **Simple Dependency Resolution** — Declare module dependencies in manifests for automated resolution
- [ ] **Cryptographic Signing** — GPG/Sigstore signing for verified modules
- [ ] **Lightweight API** — Optional REST API for faster queries
- [ ] **Search & Discovery UI** — Web interface for browsing modules
- [ ] **Module Analytics** — Opt-in usage tracking (when needed)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Submitting a Module

1. **Prepare your module** — Ensure it follows amplifier-foundation conventions
2. **Create manifest** — Use [examples/manifest.example.yaml](./examples/manifest.example.yaml) as template
3. **Validate locally** — `python scripts/validate_manifest.py your-manifest.yaml`
4. **Submit PR** — Add to `registry/modules/your-module-name/manifest.yaml`
5. **CI validation** — Automated checks run on your PR
6. **Merge** — Your module appears in the registry index

### Requesting Verification

For verified status (✓ badge), see [GOVERNANCE.md](./GOVERNANCE.md#module-verification) and use our [verification request template](./.github/ISSUE_TEMPLATE/verification-request.md).

**Requirements**:
- Product definition (audience, problem, solution)
- >70% test coverage
- Documentation
- 10-day SLA review by Microsoft OCTO MADE team

### Reporting Issues

Found a problematic module? [Open an issue](https://github.com/microsoft/amplifier-module-registry/issues) with details about:
- Module manifest errors or validation issues
- Broken source repository links
- Incompatibility with current amplifier-foundation versions
- Security concerns

We'll flag modules appropriately. Automated compatibility checks run weekly.

## 📜 License

This registry is MIT licensed. Individual modules may have their own licenses — check each module's manifest.

---

**Questions?** Open an issue or reach out to the amplifier-foundation team.
