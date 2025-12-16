"""
Tests for validate_manifest.py script.
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_manifest import ManifestValidator


class TestManifestValidator:
    """Test suite for ManifestValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ManifestValidator()

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_load_valid_yaml_manifest(self, validator, fixtures_dir):
        """Test loading a valid YAML manifest."""
        manifest_path = fixtures_dir / "valid" / "agent-example.yaml"
        manifest = validator.load_manifest(manifest_path)

        assert manifest is not None
        assert manifest["name"] == "test-agent"
        assert manifest["version"] == "1.0.0"
        assert manifest["module_type"] == "agent"

    def test_load_embedded_manifest(self, validator, fixtures_dir):
        """Test loading manifest with embedded repository type."""
        manifest_path = fixtures_dir / "valid" / "embedded-example.yaml"
        manifest = validator.load_manifest(manifest_path)

        assert manifest["repository"]["type"] == "embedded"

    def test_validate_valid_agent_manifest(self, validator, fixtures_dir):
        """Test that a valid agent manifest passes validation."""
        manifest_path = fixtures_dir / "valid" / "agent-example.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        assert is_valid
        assert len(errors) == 0

    def test_validate_valid_behavior_manifest(self, validator, fixtures_dir):
        """Test that a valid behavior manifest passes validation."""
        manifest_path = fixtures_dir / "valid" / "behavior-example.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        assert is_valid
        assert len(errors) == 0

    def test_missing_required_fields(self, validator, fixtures_dir):
        """Test that missing required fields causes validation failure."""
        manifest_path = fixtures_dir / "invalid" / "missing-required.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        assert not is_valid
        assert len(errors) > 0

    def test_invalid_semver_format(self, validator, fixtures_dir):
        """Test that invalid semver format is rejected."""
        manifest_path = fixtures_dir / "invalid" / "invalid-semver.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        assert not is_valid
        assert any("version" in err.lower() for err in errors)

    def test_invalid_entry_point_format(self, validator, fixtures_dir):
        """Test that invalid entry point format is rejected."""
        manifest_path = fixtures_dir / "invalid" / "bad-entry-point.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        assert not is_valid
        assert any("entry_point" in err.lower() for err in errors)

    def test_reserved_namespace_warning(self, validator, fixtures_dir):
        """Test that reserved namespace generates warning."""
        manifest_path = fixtures_dir / "invalid" / "bad-namespace.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        # Should be valid but generate warning
        assert is_valid
        assert len(warnings) > 0
        assert any("reserved" in warn.lower() for warn in warnings)

    def test_validate_namespace_function(self, validator):
        """Test namespace validation function."""
        # Reserved namespace should warn
        assert validator.validate_namespace("amplifier-test")
        assert len(validator.warnings) > 0

        # Non-reserved should pass without warning
        validator.warnings = []
        assert validator.validate_namespace("my-module")
        assert len(validator.warnings) == 0

    def test_validate_entry_point_formats(self, validator):
        """Test various entry point format validations."""
        # Valid formats
        assert validator.validate_entry_point("module:Class")
        assert validator.validate_entry_point("package.module:Class")
        assert validator.validate_entry_point("deep.package.module:MyClass")

        validator.errors = []

        # Invalid formats
        assert not validator.validate_entry_point("no-colon")
        assert not validator.validate_entry_point(":no-module")
        assert not validator.validate_entry_point("module:")
        assert not validator.validate_entry_point("123invalid:Class")

    def test_validate_version_constraints(self, validator):
        """Test version constraint validation."""
        # Valid constraints
        manifest_valid = {
            "foundation_version": ">=0.1.0",
            "dependencies": {
                "modules": ["other-module>=1.0.0"]
            }
        }
        assert validator.validate_version_constraints(manifest_valid)

        # Invalid constraint
        validator.errors = []
        manifest_invalid = {
            "foundation_version": "not-a-version",
        }
        assert not validator.validate_version_constraints(manifest_invalid)
        assert len(validator.errors) > 0

    def test_validate_repository_git(self, validator):
        """Test repository validation for git type."""
        # Git repo requires URL
        manifest_no_url = {
            "repository": {
                "type": "git"
            }
        }
        assert not validator.validate_repository(manifest_no_url)

        # Git repo with URL should pass
        validator.errors = []
        manifest_with_url = {
            "repository": {
                "type": "git",
                "url": "https://github.com/user/repo"
            }
        }
        assert validator.validate_repository(manifest_with_url)

    def test_validate_repository_embedded(self, validator):
        """Test repository validation for embedded type."""
        # Embedded doesn't require URL
        manifest_embedded = {
            "repository": {
                "type": "embedded"
            }
        }
        assert validator.validate_repository(manifest_embedded)

    def test_semantic_rules_missing_github(self, validator, fixtures_dir):
        """Test that missing GitHub username generates warning."""
        manifest_path = fixtures_dir / "valid" / "embedded-example.yaml"
        is_valid, errors, warnings = validator.validate(manifest_path)

        # Should be valid but warn about missing github
        assert is_valid
        assert any("github" in warn.lower() for warn in warnings)

    def test_semantic_rules_short_description(self, validator):
        """Test warning for short description."""
        manifest = {
            "description": "Too short"
        }
        validator.validate_semantic_rules(manifest)

        assert len(validator.warnings) > 0
        assert any("description" in warn.lower() for warn in validator.warnings)

    def test_semantic_rules_no_tags(self, validator):
        """Test warning when no tags provided."""
        manifest = {
            "description": "This is a long enough description for testing",
            "author": {"name": "Test", "github": "test"}
        }
        validator.validate_semantic_rules(manifest)

        assert any("tags" in warn.lower() or "tag" in warn.lower()
                   for warn in validator.warnings)


class TestValidationIntegration:
    """Integration tests for full validation workflow."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path."""
        return Path(__file__).parent / "fixtures"

    def test_all_valid_fixtures_pass(self, fixtures_dir):
        """Test that all valid fixtures pass validation."""
        validator = ManifestValidator()
        valid_dir = fixtures_dir / "valid"

        for manifest_file in valid_dir.glob("*.yaml"):
            is_valid, errors, warnings = validator.validate(manifest_file)
            assert is_valid, f"{manifest_file.name} should be valid but got errors: {errors}"

    def test_all_invalid_fixtures_fail_or_warn(self, fixtures_dir):
        """Test that all invalid fixtures fail validation or generate warnings."""
        validator = ManifestValidator()
        invalid_dir = fixtures_dir / "invalid"

        for manifest_file in invalid_dir.glob("*.yaml"):
            is_valid, errors, warnings = validator.validate(manifest_file)

            # Should either fail or have warnings
            assert not is_valid or len(warnings) > 0, \
                f"{manifest_file.name} should fail or warn but passed silently"


class TestCLIBehavior:
    """Test CLI-specific behavior."""

    def test_validator_resets_state(self):
        """Test that validator resets errors/warnings between validations."""
        validator = ManifestValidator()

        # First validation with errors
        manifest_bad = {
            "repository": {"type": "git"}
        }
        validator.validate_repository(manifest_bad)
        assert len(validator.errors) > 0

        # Create new path for second validation
        fixtures_dir = Path(__file__).parent / "fixtures"
        manifest_path = fixtures_dir / "valid" / "agent-example.yaml"

        # Second validation should reset state
        is_valid, errors, warnings = validator.validate(manifest_path)
        # This one is valid, so should have no errors from first validation
        assert is_valid
        assert len(errors) == 0
