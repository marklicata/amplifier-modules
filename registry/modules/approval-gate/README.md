# Approval Gate Behavior

A reusable behavior module for Amplifier that adds human approval gates to agent workflows.

## Overview

The Approval Gate behavior pauses workflow execution and waits for human approval before proceeding. Perfect for:
- Sensitive operations requiring human oversight
- Multi-step workflows with review points
- Compliance and audit requirements
- Testing and validation gates

## Installation

```bash
amplifier module install approval-gate
```

## Usage

### Basic Approval Gate

```python
from approval_gate.behavior import ApprovalGateBehavior

gate = ApprovalGateBehavior(
    prompt="Approve deployment to production?",
    timeout_seconds=300
)

approved = gate.wait_for_approval()
if approved:
    # Continue with workflow
    deploy_to_production()
```

### In a Workflow YAML

```yaml
steps:
  - name: Build application
    agent: builder

  - name: Review build
    behavior: approval-gate
    config:
      prompt: "Review build artifacts before deployment?"
      timeout_seconds: 600
      required_approvers: 2

  - name: Deploy
    agent: deployer
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prompt` | string | Required | Message shown to approvers |
| `timeout_seconds` | integer | `300` | Max wait time before auto-rejection |
| `required_approvers` | integer | `1` | Number of approvals needed |
| `notify_channels` | list | `[]` | Channels to notify (email, slack, etc) |
| `auto_approve_conditions` | dict | `{}` | Conditions for automatic approval |

## Features

- **Flexible Timeouts**: Configure how long to wait for approval
- **Multi-Approver Support**: Require multiple people to approve
- **Notification Integration**: Send alerts via email, Slack, Teams
- **Context Preservation**: Maintains workflow state during approval wait
- **Audit Logging**: Records who approved and when

## Example: Conditional Auto-Approval

```yaml
behavior: approval-gate
config:
  prompt: "Deploy to staging?"
  auto_approve_conditions:
    branch: main
    tests_passing: true
    author_role: developer
```

## Contributing

Community contributions welcome! Please see [CONTRIBUTING.md](https://github.com/devtoolscontributor/amplifier-approval-gate/blob/main/CONTRIBUTING.md).

## License

MIT License
