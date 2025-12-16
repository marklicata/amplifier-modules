"""
Tests for generate_index.py script.
"""

import json
import sys
from pathlib import Path
import tempfile
import shutil

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_index import (
    load_manifest,
    scan_registry,
    load_module_manifest,
    generate_index
)


class TestLoadManifest:
    """Test manifest loading functionality."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures" / "valid"

    def test_load_yaml_manifest(self, fixtures_dir):
        """Test loading YAML manifest."""
        manifest_path = fixtures_dir / "agent-example.yaml"
        manifest = load_manifest(manifest_path)

        assert manifest is not None
        assert manifest["name"] == "test-agent"
        assert manifest["version"] == "1.0.0"

    def test_load_yaml_with_dependencies(self, fixtures_dir):
        """Test loading manifest with dependencies."""
        manifest_path = fixtures_dir / "agent-example.yaml"
        manifest = load_manifest(manifest_path)

        assert "dependencies" in manifest
        assert "python" in manifest["dependencies"]
        assert len(manifest["dependencies"]["python"]) > 0


class TestLoadModuleManifest:
    """Test loading module manifest with version info."""

    def test_load_module_from_community(self, tmp_path):
        """Test loading a community module."""
        # Create test module structure
        module_dir = tmp_path / "test-module"
        module_dir.mkdir()

        manifest_content = """
name: test-module
version: 1.0.0
description: Test module for unit testing
author:
  name: Test Author
  github: testauthor
module_type: agent
entry_point: test_module:TestAgent
repository:
  type: git
  url: https://github.com/test/test-module
tags:
  - test
"""
        (module_dir / "manifest.yaml").write_text(manifest_content)

        result = load_module_manifest(module_dir, verified=False)

        assert result is not None
        assert result["name"] == "test-module"
        assert result["latest"] == "1.0.0"
        assert result["verified"] is False
        assert result["module_type"] == "agent"
        assert "test" in result["tags"]

    def test_load_verified_module(self, tmp_path):
        """Test loading a verified module."""
        module_dir = tmp_path / "verified-module"
        module_dir.mkdir()

        manifest_content = """
name: verified-module
version: 2.0.0
description: Verified test module
author:
  name: Core Team
  github: microsoft
module_type: provider
entry_point: verified:Provider
repository:
  type: git
  url: https://github.com/microsoft/verified-module
"""
        (module_dir / "manifest.yaml").write_text(manifest_content)

        result = load_module_manifest(module_dir, verified=True)

        assert result["verified"] is True
        assert result["name"] == "verified-module"

    def test_load_module_with_versions_directory(self, tmp_path):
        """Test loading module with multiple versions."""
        module_dir = tmp_path / "multi-version"
        module_dir.mkdir()
        versions_dir = module_dir / "versions"
        versions_dir.mkdir()

        # Current version
        manifest_content = """
name: multi-version
version: 2.1.0
description: Module with multiple versions
author:
  name: Test
module_type: behavior
entry_point: multi:Behavior
repository:
  type: git
  url: https://github.com/test/multi
"""
        (module_dir / "manifest.yaml").write_text(manifest_content)

        # Old versions
        (versions_dir / "1.0.0.yaml").write_text("version: 1.0.0")
        (versions_dir / "2.0.0.yaml").write_text("version: 2.0.0")

        result = load_module_manifest(module_dir, verified=False)

        assert result["latest"] == "2.1.0"
        assert "1.0.0" in result["versions"]
        assert "2.0.0" in result["versions"]
        assert "2.1.0" in result["versions"]
        assert len(result["versions"]) == 3

    def test_load_module_no_manifest(self, tmp_path):
        """Test handling directory without manifest."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = load_module_manifest(empty_dir, verified=False)

        assert result is None

    def test_version_sorting(self, tmp_path):
        """Test that versions are sorted correctly (semver)."""
        module_dir = tmp_path / "versioned"
        module_dir.mkdir()
        versions_dir = module_dir / "versions"
        versions_dir.mkdir()

        manifest_content = """
name: versioned
version: 0.9.0
description: Test version sorting
author:
  name: Test
module_type: agent
entry_point: versioned:Agent
repository:
  type: git
  url: https://github.com/test/versioned
"""
        (module_dir / "manifest.yaml").write_text(manifest_content)

        # Add versions in random order
        (versions_dir / "0.1.0.yaml").write_text("version: 0.1.0")
        (versions_dir / "1.0.0.yaml").write_text("version: 1.0.0")
        (versions_dir / "0.5.0.yaml").write_text("version: 0.5.0")

        result = load_module_manifest(module_dir, verified=False)

        # Should be sorted descending (latest first)
        assert result["versions"][0] == "1.0.0"
        assert result["versions"][1] == "0.9.0"
        assert result["versions"][2] == "0.5.0"
        assert result["versions"][3] == "0.1.0"


class TestScanRegistry:
    """Test registry scanning functionality."""

    def test_scan_empty_registry(self, tmp_path):
        """Test scanning an empty registry."""
        # Create empty registry structure
        registry_dir = tmp_path / "registry"
        (registry_dir / "modules").mkdir(parents=True)
        (registry_dir / "verified").mkdir(parents=True)

        modules = scan_registry(registry_dir)

        assert modules == {}

    def test_scan_registry_with_modules(self, tmp_path):
        """Test scanning registry with community modules."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        modules_dir.mkdir(parents=True)

        # Create test module
        module1_dir = modules_dir / "module-one"
        module1_dir.mkdir()
        (module1_dir / "manifest.yaml").write_text("""
name: module-one
version: 1.0.0
description: First test module
author:
  name: Test
module_type: agent
entry_point: module_one:Agent
repository:
  type: git
  url: https://github.com/test/module-one
""")

        modules = scan_registry(registry_dir)

        assert len(modules) == 1
        assert "module-one" in modules
        assert modules["module-one"]["verified"] is False

    def test_scan_registry_with_verified_modules(self, tmp_path):
        """Test scanning registry with verified modules."""
        registry_dir = tmp_path / "registry"
        verified_dir = registry_dir / "verified"
        verified_dir.mkdir(parents=True)

        # Create verified module
        verified_module = verified_dir / "verified-one"
        verified_module.mkdir()
        (verified_module / "manifest.yaml").write_text("""
name: verified-one
version: 2.0.0
description: Verified test module
author:
  name: Core Team
  github: microsoft
module_type: provider
entry_point: verified_one:Provider
repository:
  type: git
  url: https://github.com/microsoft/verified-one
""")

        modules = scan_registry(registry_dir)

        assert len(modules) == 1
        assert "verified-one" in modules
        assert modules["verified-one"]["verified"] is True

    def test_scan_registry_mixed_modules(self, tmp_path):
        """Test scanning registry with both community and verified modules."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        verified_dir = registry_dir / "verified"
        modules_dir.mkdir(parents=True)
        verified_dir.mkdir(parents=True)

        # Community module
        (modules_dir / "community-mod").mkdir()
        (modules_dir / "community-mod" / "manifest.yaml").write_text("""
name: community-mod
version: 1.0.0
description: Community module
author:
  name: Community
module_type: behavior
entry_point: community:Mod
repository:
  type: git
  url: https://github.com/user/community-mod
""")

        # Verified module
        (verified_dir / "verified-mod").mkdir()
        (verified_dir / "verified-mod" / "manifest.yaml").write_text("""
name: verified-mod
version: 1.0.0
description: Verified module
author:
  name: Core
module_type: agent
entry_point: verified:Mod
repository:
  type: git
  url: https://github.com/core/verified-mod
""")

        modules = scan_registry(registry_dir)

        assert len(modules) == 2
        assert modules["community-mod"]["verified"] is False
        assert modules["verified-mod"]["verified"] is True


class TestGenerateIndex:
    """Test index generation functionality."""

    def test_generate_index_structure(self, tmp_path):
        """Test that generated index has correct structure."""
        registry_dir = tmp_path / "registry"
        (registry_dir / "modules").mkdir(parents=True)
        (registry_dir / "verified").mkdir(parents=True)

        index = generate_index(registry_dir)

        assert "version" in index
        assert "generated_at" in index
        assert "total_modules" in index
        assert "modules" in index
        assert "namespaces" in index
        assert "stats" in index

    def test_generate_index_empty_registry(self, tmp_path):
        """Test index generation for empty registry."""
        registry_dir = tmp_path / "registry"
        (registry_dir / "modules").mkdir(parents=True)
        (registry_dir / "verified").mkdir(parents=True)

        index = generate_index(registry_dir)

        assert index["total_modules"] == 0
        assert index["modules"] == {}
        assert index["stats"]["verified_count"] == 0
        assert index["stats"]["community_count"] == 0

    def test_generate_index_with_modules(self, tmp_path):
        """Test index generation with actual modules."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        modules_dir.mkdir(parents=True)

        # Create test modules
        for i in range(3):
            module_dir = modules_dir / f"test-module-{i}"
            module_dir.mkdir()
            (module_dir / "manifest.yaml").write_text(f"""
name: test-module-{i}
version: 1.0.{i}
description: Test module number {i}
author:
  name: Test Author
module_type: agent
entry_point: test{i}:Agent
repository:
  type: git
  url: https://github.com/test/module-{i}
""")

        index = generate_index(registry_dir)

        assert index["total_modules"] == 3
        assert len(index["modules"]) == 3
        assert index["stats"]["community_count"] == 3

    def test_generate_index_stats_by_type(self, tmp_path):
        """Test that stats are calculated by module type."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        modules_dir.mkdir(parents=True)

        # Create modules of different types
        types = ["agent", "behavior", "provider"]
        for mtype in types:
            module_dir = modules_dir / f"test-{mtype}"
            module_dir.mkdir()
            (module_dir / "manifest.yaml").write_text(f"""
name: test-{mtype}
version: 1.0.0
description: Test {mtype} module
author:
  name: Test
module_type: {mtype}
entry_point: test:Class
repository:
  type: git
  url: https://github.com/test/{mtype}
""")

        index = generate_index(registry_dir)

        assert index["stats"]["by_type"]["agent"] == 1
        assert index["stats"]["by_type"]["behavior"] == 1
        assert index["stats"]["by_type"]["provider"] == 1

    def test_namespace_claiming(self, tmp_path):
        """Test that namespaces are claimed correctly."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        modules_dir.mkdir(parents=True)

        # Create module with custom prefix
        module_dir = modules_dir / "custom-module"
        module_dir.mkdir()
        (module_dir / "manifest.yaml").write_text("""
name: custom-module
version: 1.0.0
description: Module with custom namespace
author:
  name: Test Author
  github: customdev
module_type: agent
entry_point: custom:Module
repository:
  type: git
  url: https://github.com/customdev/custom-module
""")

        index = generate_index(registry_dir)

        # "custom" should be claimed by customdev
        assert "custom" in index["namespaces"]["claimed"]
        assert index["namespaces"]["claimed"]["custom"] == "customdev"

    def test_reserved_namespaces_not_claimed(self, tmp_path):
        """Test that reserved namespaces are not claimed."""
        registry_dir = tmp_path / "registry"
        modules_dir = registry_dir / "modules"
        modules_dir.mkdir(parents=True)

        index = generate_index(registry_dir)

        # Reserved namespaces should be listed
        assert "amplifier" in index["namespaces"]["reserved"]
        assert "microsoft" in index["namespaces"]["reserved"]
        assert "azure" in index["namespaces"]["reserved"]
