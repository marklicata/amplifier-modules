#!/usr/bin/env python3
"""
Manifest validation script for amplifier-modules registry.

Validates module manifests against the JSON schema and performs
additional semantic checks.
"""

import json
import sys
import re
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("ERROR: jsonschema package required. Install with: pip install jsonschema")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None  # YAML support optional


# Reserved namespaces for official Microsoft/core team modules
RESERVED_NAMESPACES = [
    "amplifier",
    "amp",
    "microsoft",
    "msft",
    "azure",
    "official",
    "core",
    "foundation",
]


class ManifestValidator:
    """Validates module manifests for the amplifier-modules registry."""

    def __init__(self, schema_path: Optional[Path] = None):
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schemas" / "module-manifest.schema.json"
        
        with open(schema_path) as f:
            self.schema = json.load(f)
        
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def load_manifest(self, path: Path) -> dict:
        """Load manifest from YAML or JSON file."""
        content = path.read_text(encoding="utf-8")
        
        if path.suffix in (".yml", ".yaml"):
            if yaml is None:
                raise ImportError("PyYAML required for YAML manifests: pip install pyyaml")
            return yaml.safe_load(content)
        else:
            return json.loads(content)

    def validate_schema(self, manifest: dict) -> bool:
        """Validate manifest against JSON schema."""
        try:
            validate(instance=manifest, schema=self.schema)
            return True
        except ValidationError as e:
            self.errors.append(f"Schema validation failed: {e.message}")
            if e.path:
                self.errors.append(f"  Path: {'.'.join(str(p) for p in e.path)}")
            return False

    def validate_namespace(self, name: str, author_github: Optional[str] = None) -> bool:
        """Check namespace reservation rules."""
        prefix = name.split("-")[0]
        
        if prefix in RESERVED_NAMESPACES:
            # For now, we just warn - actual enforcement happens in CI
            self.warnings.append(
                f"Module name '{name}' uses reserved namespace '{prefix}'. "
                "Only core team members can publish to reserved namespaces."
            )
        
        return True

    def validate_entry_point(self, entry_point: str) -> bool:
        """Validate entry point format and basic sanity."""
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*:[a-zA-Z_][a-zA-Z0-9_]*$"
        
        if not re.match(pattern, entry_point):
            self.errors.append(
                f"Invalid entry_point format: '{entry_point}'. "
                "Expected format: 'module.path:ClassName' (e.g., 'my_agent.main:MyAgent')"
            )
            return False
        
        return True

    def validate_version_constraints(self, manifest: dict) -> bool:
        """Validate version constraint formats."""
        valid = True
        
        # Check foundation_version
        if fv := manifest.get("foundation_version"):
            if not re.match(r"^(>=|<=|~=|==|\^)?\d+\.\d+(\.\d+)?$", fv):
                self.errors.append(f"Invalid foundation_version constraint: '{fv}'")
                valid = False
        
        # Check module dependencies
        if deps := manifest.get("dependencies", {}).get("modules", []):
            for dep in deps:
                if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]((>=|<=|~=|==|\^)\d+\.\d+(\.\d+)?)?$", dep):
                    self.errors.append(f"Invalid module dependency format: '{dep}'")
                    valid = False
        
        return valid

    def validate_repository(self, manifest: dict) -> bool:
        """Validate repository configuration."""
        repo = manifest.get("repository", {})
        repo_type = repo.get("type", "git")
        
        if repo_type == "git" and not repo.get("url"):
            self.errors.append("Repository URL required when type is 'git'")
            return False
        
        if repo_type == "git" and repo.get("url"):
            url = repo["url"]
            if not (url.startswith("https://") or url.startswith("git@")):
                self.warnings.append(
                    f"Repository URL '{url}' should use HTTPS or SSH format"
                )
        
        return True

    def validate_semantic_rules(self, manifest: dict) -> bool:
        """Additional semantic validations beyond schema."""
        valid = True
        
        # Verify author info completeness
        author = manifest.get("author", {})
        if not author.get("github"):
            self.warnings.append(
                "Author GitHub username recommended for attribution and contact"
            )
        
        # Check for description quality
        desc = manifest.get("description", "")
        if len(desc) < 20:
            self.warnings.append(
                "Description is quite short. Consider adding more detail for discoverability."
            )
        
        # Validate tags
        tags = manifest.get("tags", [])
        if not tags:
            self.warnings.append(
                "Adding tags improves module discoverability"
            )
        
        # Check license
        if not manifest.get("license"):
            self.warnings.append(
                "No license specified. Defaults to MIT but explicit is better."
            )
        
        return valid

    def validate(self, manifest_path: Path) -> tuple[bool, list[str], list[str]]:
        """
        Run full validation on a manifest file.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Load manifest
        try:
            manifest = self.load_manifest(manifest_path)
        except Exception as e:
            self.errors.append(f"Failed to load manifest: {e}")
            return False, self.errors, self.warnings
        
        # Run all validations
        schema_valid = self.validate_schema(manifest)
        
        if schema_valid:
            # Only run semantic checks if schema is valid
            self.validate_namespace(
                manifest.get("name", ""),
                manifest.get("author", {}).get("github")
            )
            self.validate_entry_point(manifest.get("entry_point", ""))
            self.validate_version_constraints(manifest)
            self.validate_repository(manifest)
            self.validate_semantic_rules(manifest)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate amplifier module manifests"
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to manifest file (YAML or JSON)"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Custom schema path (optional)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    if not args.manifest.exists():
        print(f"ERROR: Manifest file not found: {args.manifest}")
        sys.exit(1)
    
    validator = ManifestValidator(args.schema)
    is_valid, errors, warnings = validator.validate(args.manifest)
    
    if args.strict and warnings:
        is_valid = False
        errors.extend([f"[strict] {w}" for w in warnings])
        warnings = []
    
    if args.json:
        result = {
            "valid": is_valid,
            "manifest": str(args.manifest),
            "errors": errors,
            "warnings": warnings,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }
        print(json.dumps(result, indent=2))
    else:
        if is_valid:
            print(f"[OK] Manifest valid: {args.manifest}")
        else:
            print(f"[FAIL] Manifest invalid: {args.manifest}")
        
        for error in errors:
            print(f"  ERROR: {error}")
        
        for warning in warnings:
            print(f"  WARN: {warning}")
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
