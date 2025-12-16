#!/usr/bin/env python3
"""
Compatibility checker for amplifier-modules registry.

Checks if modules are compatible with a given amplifier-foundation version.
Can update module status and create GitHub issues for broken modules.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List
import argparse

try:
    from packaging import version
    from packaging.specifiers import SpecifierSet, InvalidSpecifier
except ImportError:
    print("ERROR: packaging module required. Install with: pip install packaging")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None


class CompatibilityChecker:
    """Check module compatibility with amplifier-foundation versions."""

    def __init__(self, foundation_version: str, registry_path: Path):
        self.foundation_version = foundation_version
        self.registry_path = registry_path
        self.broken_modules: List[Dict] = []
        self.compatible_modules: List[str] = []
        self.warnings: List[str] = []

    def load_manifest(self, path: Path) -> Optional[dict]:
        """Load a manifest file (YAML or JSON)."""
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix in (".yml", ".yaml"):
                if yaml is None:
                    raise ImportError("PyYAML required for YAML manifests")
                return yaml.safe_load(content)
            return json.loads(content)
        except Exception as e:
            self.warnings.append(f"Failed to load {path}: {e}")
            return None

    def check_version_constraint(self, module_name: str, constraint: str) -> bool:
        """
        Check if foundation_version satisfies the module's version constraint.

        Args:
            module_name: Name of the module being checked
            constraint: Version constraint string (e.g., ">=0.1.0", "~=1.2.0")

        Returns:
            True if compatible, False otherwise
        """
        if not constraint:
            # No constraint specified - assume compatible
            return True

        try:
            spec = SpecifierSet(constraint)
            is_compatible = self.foundation_version in spec

            if not is_compatible:
                self.broken_modules.append({
                    "module": module_name,
                    "reason": f"Version constraint not met",
                    "constraint": constraint,
                    "foundation_version": self.foundation_version,
                    "severity": "high"
                })

            return is_compatible

        except InvalidSpecifier as e:
            self.warnings.append(
                f"Invalid version constraint in {module_name}: {constraint} ({e})"
            )
            return True  # Assume compatible if constraint is invalid

    def check_module_import(self, module_name: str, entry_point: str) -> bool:
        """
        Attempt to import module entry point (if module is installed).

        Args:
            module_name: Name of the module
            entry_point: Python entry point string (e.g., "my_module:MyClass")

        Returns:
            True if import succeeds or module not installed, False if import fails
        """
        if ":" not in entry_point:
            return True

        module_path, class_name = entry_point.split(":", 1)

        try:
            # Try to import the module
            __import__(module_path)
            return True
        except ImportError:
            # Module not installed - can't check import, assume compatible
            return True
        except Exception as e:
            # Import failed for other reason - likely incompatible
            self.broken_modules.append({
                "module": module_name,
                "reason": f"Import failed: {type(e).__name__}: {e}",
                "entry_point": entry_point,
                "foundation_version": self.foundation_version,
                "severity": "critical"
            })
            return False

    def check_module(self, module_dir: Path, is_verified: bool) -> Dict:
        """
        Check compatibility of a single module.

        Returns:
            Dict with compatibility result
        """
        # Find manifest
        manifest_path = None
        for name in ["manifest.yaml", "manifest.yml", "manifest.json"]:
            candidate = module_dir / name
            if candidate.exists():
                manifest_path = candidate
                break

        if not manifest_path:
            return {"compatible": False, "reason": "No manifest found"}

        manifest = self.load_manifest(manifest_path)
        if not manifest:
            return {"compatible": False, "reason": "Failed to load manifest"}

        module_name = manifest.get("name", module_dir.name)
        foundation_constraint = manifest.get("foundation_version")
        entry_point = manifest.get("entry_point")

        # Check version constraint
        constraint_ok = self.check_version_constraint(module_name, foundation_constraint)

        # Check import (if applicable)
        import_ok = self.check_module_import(module_name, entry_point) if entry_point else True

        compatible = constraint_ok and import_ok

        if compatible:
            self.compatible_modules.append(module_name)

        return {
            "compatible": compatible,
            "module": module_name,
            "constraint": foundation_constraint,
            "entry_point": entry_point,
            "is_verified": is_verified
        }

    def scan_registry(self) -> Dict:
        """
        Scan entire registry and check all modules.

        Returns:
            Summary dict with results
        """
        checked = 0

        # Check community modules
        modules_dir = self.registry_path / "modules"
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir() and module_dir.name != ".gitkeep":
                    self.check_module(module_dir, is_verified=False)
                    checked += 1

        # Check verified modules
        verified_dir = self.registry_path / "verified"
        if verified_dir.exists():
            for module_dir in verified_dir.iterdir():
                if module_dir.is_dir() and module_dir.name != ".gitkeep":
                    self.check_module(module_dir, is_verified=True)
                    checked += 1

        return {
            "foundation_version": self.foundation_version,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "total_checked": checked,
            "compatible": len(self.compatible_modules),
            "broken": len(self.broken_modules),
            "warnings": len(self.warnings)
        }

    def update_module_status(self, module_name: str, status: str, reason: str = None):
        """
        Update module manifest status field.

        Args:
            module_name: Name of the module
            status: New status (active, broken, deprecated, archived)
            reason: Optional reason for status change
        """
        # Find module directory
        for base_dir in ["modules", "verified"]:
            module_dir = self.registry_path / base_dir / module_name
            if not module_dir.exists():
                continue

            # Find manifest
            manifest_path = None
            for name in ["manifest.yaml", "manifest.yml"]:
                candidate = module_dir / name
                if candidate.exists():
                    manifest_path = candidate
                    break

            if not manifest_path:
                continue

            # Load manifest
            manifest = self.load_manifest(manifest_path)
            if not manifest:
                continue

            # Update status
            manifest["status"] = status
            if reason:
                manifest["status_message"] = reason

            # Write back
            if yaml:
                content = yaml.dump(manifest, default_flow_style=False, sort_keys=False)
                manifest_path.write_text(content, encoding="utf-8")
                print(f"Updated {module_name} status to: {status}")
            else:
                print(f"Cannot update {module_name}: PyYAML not available")

    def write_broken_report(self, output_path: Path):
        """Write report of broken modules to JSON file."""
        report = {
            "foundation_version": self.foundation_version,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "broken_modules": self.broken_modules
        }

        output_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8"
        )
        print(f"Wrote broken modules report to: {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check module compatibility with amplifier-foundation"
    )
    parser.add_argument(
        "--foundation-version",
        required=True,
        help="Version of amplifier-foundation to check against (e.g., '0.5.0')"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).parent.parent / "registry",
        help="Path to registry directory"
    )
    parser.add_argument(
        "--update-status",
        action="store_true",
        help="Update module manifest status for broken modules"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write broken modules report to file (JSON)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    if not args.registry.exists():
        print(f"ERROR: Registry directory not found: {args.registry}")
        sys.exit(1)

    # Run compatibility check
    checker = CompatibilityChecker(args.foundation_version, args.registry)
    summary = checker.scan_registry()

    # Update status if requested
    if args.update_status:
        for broken in checker.broken_modules:
            module_name = broken["module"]
            reason = broken["reason"]
            checker.update_module_status(module_name, "broken", reason)

    # Write broken report if requested
    if args.output:
        checker.write_broken_report(args.output)

    # Output results
    if args.json:
        result = {
            **summary,
            "broken_modules": checker.broken_modules,
            "compatible_modules": checker.compatible_modules,
            "warnings": checker.warnings
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\nCompatibility Check Results")
        print(f"===========================")
        print(f"Foundation Version: {args.foundation_version}")
        print(f"Total Modules: {summary['total_checked']}")
        print(f"Compatible: {summary['compatible']}")
        print(f"Broken: {summary['broken']}")

        if checker.broken_modules:
            print(f"\nBroken Modules:")
            for broken in checker.broken_modules:
                print(f"  - {broken['module']}: {broken['reason']}")

        if checker.warnings:
            print(f"\nWarnings:")
            for warning in checker.warnings:
                print(f"  - {warning}")

    # Exit with error code if there are broken modules
    sys.exit(1 if checker.broken_modules else 0)


if __name__ == "__main__":
    main()
