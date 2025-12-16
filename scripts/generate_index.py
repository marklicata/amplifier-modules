#!/usr/bin/env python3
"""
Registry index generator for amplifier-modules.

Scans the registry directory and generates a consolidated index.json
for fast lookups and CLI discovery.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


def load_manifest(path: Path) -> dict:
    """Load a manifest file (YAML or JSON)."""
    content = path.read_text(encoding="utf-8")
    
    if path.suffix in (".yml", ".yaml"):
        if yaml is None:
            raise ImportError("PyYAML required: pip install pyyaml")
        return yaml.safe_load(content)
    return json.loads(content)


def scan_registry(registry_path: Path) -> dict:
    """
    Scan registry directory structure and build index.
    
    Expected structure:
        registry/
            modules/
                module-name/
                    manifest.yaml (or manifest.json)
                    versions/
                        1.0.0.yaml
                        1.1.0.yaml
            verified/
                verified-module/
                    manifest.yaml
    """
    modules = {}
    
    # Scan community modules
    modules_dir = registry_path / "modules"
    if modules_dir.exists():
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir():
                manifest = load_module_manifest(module_dir, verified=False)
                if manifest:
                    modules[manifest["name"]] = manifest
    
    # Scan verified modules
    verified_dir = registry_path / "verified"
    if verified_dir.exists():
        for module_dir in verified_dir.iterdir():
            if module_dir.is_dir():
                manifest = load_module_manifest(module_dir, verified=True)
                if manifest:
                    modules[manifest["name"]] = manifest
    
    return modules


def load_module_manifest(module_dir: Path, verified: bool) -> Optional[dict]:
    """Load manifest and version info for a single module."""
    # Find manifest file
    manifest_path = None
    for name in ["manifest.yaml", "manifest.yml", "manifest.json"]:
        candidate = module_dir / name
        if candidate.exists():
            manifest_path = candidate
            break
    
    if not manifest_path:
        print(f"WARN: No manifest found in {module_dir}", file=sys.stderr)
        return None
    
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        print(f"WARN: Failed to load {manifest_path}: {e}", file=sys.stderr)
        return None
    
    # Collect available versions
    versions = [manifest.get("version", "0.0.0")]
    versions_dir = module_dir / "versions"
    if versions_dir.exists():
        for version_file in versions_dir.glob("*.yaml"):
            version = version_file.stem
            if version not in versions:
                versions.append(version)
        for version_file in versions_dir.glob("*.json"):
            version = version_file.stem
            if version not in versions:
                versions.append(version)
    
    # Sort versions (basic semver sort)
    versions.sort(key=lambda v: [int(x) for x in v.replace("-", ".").split(".")[:3]], reverse=True)
    
    # Build index entry
    return {
        "name": manifest.get("name"),
        "latest": versions[0] if versions else manifest.get("version"),
        "description": manifest.get("description", ""),
        "module_type": manifest.get("module_type"),
        "source": manifest.get("source"),
        "author": manifest.get("author", {}).get("name", "Unknown"),
        "author_github": manifest.get("author", {}).get("github"),
        "verified": verified,
        "status": manifest.get("status", "active"),
        "tags": manifest.get("tags", []),
        "downloads": manifest.get("analytics", {}).get("downloads", 0),
        "versions": versions,
        "license": manifest.get("license", "MIT"),
        "foundation_version": manifest.get("foundation_version"),
    }


def generate_index(registry_path: Path) -> dict:
    """Generate the complete registry index."""
    modules = scan_registry(registry_path)
    
    # Load reserved namespaces from config if exists
    reserved = [
        "amplifier", "amp", "microsoft", "msft", 
        "azure", "official", "core", "foundation"
    ]
    
    # Build claimed namespaces from existing modules
    claimed = {}
    for name, module in modules.items():
        prefix = name.split("-")[0]
        if prefix not in reserved:
            owner = module.get("author_github")
            if owner and prefix not in claimed:
                claimed[prefix] = owner
    
    index = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_modules": len(modules),
        "modules": {
            name: {k: v for k, v in mod.items() if k != "name"}
            for name, mod in modules.items()
        },
        "namespaces": {
            "reserved": reserved,
            "claimed": claimed
        },
        "stats": {
            "by_type": {},
            "verified_count": sum(1 for m in modules.values() if m.get("verified")),
            "community_count": sum(1 for m in modules.values() if not m.get("verified")),
        }
    }
    
    # Count by type
    for module in modules.values():
        mtype = module.get("module_type", "unknown")
        index["stats"]["by_type"][mtype] = index["stats"]["by_type"].get(mtype, 0) + 1
    
    return index


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate registry index from module manifests"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).parent.parent / "registry",
        help="Path to registry directory"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for index.json (default: registry/index.json)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output"
    )
    
    args = parser.parse_args()
    
    if not args.registry.exists():
        print(f"ERROR: Registry directory not found: {args.registry}")
        sys.exit(1)
    
    output_path = args.output or (args.registry / "index.json")
    
    print(f"Scanning registry: {args.registry}")
    index = generate_index(args.registry)
    
    indent = 2 if args.pretty else None
    output_path.write_text(json.dumps(index, indent=indent), encoding="utf-8")
    
    print(f"Generated index: {output_path}")
    print(f"  Total modules: {index['total_modules']}")
    print(f"  Verified: {index['stats']['verified_count']}")
    print(f"  Community: {index['stats']['community_count']}")
    
    if index['stats']['by_type']:
        print("  By type:")
        for mtype, count in index['stats']['by_type'].items():
            print(f"    {mtype}: {count}")


if __name__ == "__main__":
    main()
