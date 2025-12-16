# Contributing to amplifier-modules

Thank you for your interest in contributing to the amplifier-modules registry! This document outlines the process for submitting modules and contributing to the registry infrastructure.

## 📦 Submitting a Module

### Prerequisites

Before submitting, ensure your module:

1. **Works with amplifier-foundation** — Test against a recent version
2. **Has a public repository** — Your source code must be accessible (GitHub, GitLab, etc.)
3. **Includes documentation** — At minimum, a README explaining what it does
4. **Specifies a license** — We recommend MIT, but any OSI-approved license works

### Step-by-Step Submission

#### 1. Prepare Your Manifest

Create a `manifest.yaml` following our schema. Start with the example:

```bash
cp examples/manifest.example.yaml my-module-manifest.yaml
# Edit with your module's details
```

Required fields:
- `name` — Unique identifier (lowercase, hyphens allowed)
- `version` — Semantic version (e.g., `1.0.0`)
- `description` — What your module does (10-500 chars)
- `author.name` — Your name
- `module_type` — One of: `agent`, `behavior`, `provider`, `bundle`, `context`
- `entry_point` — Python import path (e.g., `my_module.main:MyAgent`)

#### 2. Validate Locally

```bash
pip install jsonschema pyyaml
python scripts/validate_manifest.py my-module-manifest.yaml
```

Fix any errors before proceeding. Warnings are recommendations but not blockers.

#### 3. Fork and Create PR

```bash
# Fork this repo on GitHub, then:
git clone https://github.com/YOUR-USERNAME/amplifier-modules
cd amplifier-modules

# Create your module directory
mkdir -p registry/modules/your-module-name
cp my-module-manifest.yaml registry/modules/your-module-name/manifest.yaml

# Commit and push
git checkout -b add-your-module-name
git add registry/modules/your-module-name/
git commit -m "feat: add your-module-name module"
git push origin add-your-module-name
```

Then open a Pull Request against `main`.

#### 4. CI Validation

Our GitHub Actions will automatically:
- Validate your manifest against the schema
- Check for namespace conflicts
- Verify required fields

#### 5. Merge

Once CI passes, a maintainer will review and merge. Your module will appear in `registry/index.json` automatically.

## 🔄 Updating a Module

To release a new version:

1. Update `version` in your manifest
2. Optionally, copy the old manifest to `versions/X.Y.Z.yaml` for history
3. Submit a PR with the changes

## 🏷️ Naming Guidelines

### DO:
- Use lowercase letters, numbers, and hyphens
- Start with a letter
- Be descriptive: `code-reviewer`, `github-integration`, `security-scanner`
- Use your username as prefix for personal modules: `jsmith-helper`

### DON'T:
- Use reserved prefixes (`amplifier-`, `microsoft-`, `azure-`, etc.)
- Use generic names that could conflict: `helper`, `utils`, `tools`
- Include version numbers in names: `my-module-v2`

## ✅ Getting Verified Status

Verified modules get:
- A verified badge in listings
- Higher trust/visibility
- Placement in `registry/verified/`

To request verification:

1. Your module must be published in `registry/modules/` first
2. Open an issue titled "Verification Request: module-name"
3. Include:
   - Link to your module's repository
   - Evidence of testing/quality (tests, CI, usage)
   - Why verification would benefit users

The core team reviews verification requests periodically.

## 🐛 Reporting Broken Modules

If you find a module that:
- Doesn't install correctly
- Is incompatible with current amplifier-foundation
- Has security issues
- Is abandoned/unmaintained

Please [open an issue](https://github.com/microsoft/amplifier-modules/issues/new) with:
- Module name
- What's broken
- Steps to reproduce
- Your environment (Python version, OS, foundation version)

We'll flag the module and notify the author.

## 🛠️ Contributing to Registry Infrastructure

Want to improve the registry itself? Great!

### Areas for Contribution

- **Schema improvements** — Better validation rules
- **Scripts** — Enhanced tooling
- **Documentation** — Clearer guides
- **CI/CD** — Workflow improvements
- **New features** — See roadmap in README

### Development Setup

```bash
git clone https://github.com/microsoft/amplifier-modules
cd amplifier-modules
pip install jsonschema pyyaml pytest

# Run tests (when available)
pytest

# Validate example manifests
python scripts/validate_manifest.py examples/manifest.example.yaml
```

### Code Style

- Python: Follow PEP 8, use type hints
- YAML: 2-space indentation
- JSON: 2-space indentation for readable files

### Commit Messages

We use conventional commits:
- `feat: add new feature`
- `fix: correct bug`
- `docs: update documentation`
- `chore: maintenance task`

## ❓ Questions?

- **General questions** — Open a Discussion
- **Bug reports** — Open an Issue
- **Security issues** — Email security@microsoft.com (do not open public issues)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping grow the amplifier ecosystem! 🚀
