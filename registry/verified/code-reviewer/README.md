# Code Reviewer Agent

An automated code review agent for the Amplifier platform that analyzes code quality, style adherence, and identifies potential issues.

## Features

- **Style Checking**: Enforces consistent code style across your project
- **Quality Analysis**: Identifies code smells, complexity issues, and potential bugs
- **Best Practices**: Suggests improvements based on language-specific best practices
- **Customizable Rules**: Configure which checks to run and their severity levels

## Installation

```bash
amplifier module install code-reviewer
```

## Usage

### As a Standalone Agent

```python
from code_reviewer.agent import CodeReviewerAgent

agent = CodeReviewerAgent(config={
    "severity": "medium",
    "auto_fix": False
})

result = agent.review("path/to/code")
print(result.summary)
```

### In a Workflow

```yaml
steps:
  - agent: code-reviewer
    config:
      paths: ["src/"]
      exclude: ["tests/"]
      severity: high
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `severity` | string | `medium` | Minimum severity level (low/medium/high) |
| `auto_fix` | boolean | `false` | Automatically fix issues when possible |
| `paths` | list | `["."]` | Directories to analyze |
| `exclude` | list | `[]` | Patterns to exclude |

## Example Output

```
Code Review Summary
==================
Files analyzed: 47
Issues found: 12
  - High: 2
  - Medium: 7
  - Low: 3

Top Issues:
1. [HIGH] Potential SQL injection in database.py:45
2. [HIGH] Unhandled exception in api.py:123
3. [MEDIUM] Function complexity too high in utils.py:67
```

## Contributing

This is a verified module maintained by the Amplifier core team. For issues or feature requests, please visit our [GitHub repository](https://github.com/microsoft/amplifier-code-reviewer).

## License

MIT License - see LICENSE file for details
