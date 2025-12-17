# Governance

This document outlines the governance model, processes, and policies for the amplifier-module-registry registry.

---

## Table of Contents

1. [Core Team](#core-team)
2. [Module Verification](#module-verification)
3. [Namespace Management](#namespace-management)
4. [Module Lifecycle](#module-lifecycle)
5. [Breaking Changes](#breaking-changes)
6. [Dispute Resolution](#dispute-resolution)
7. [Security and Safety](#security-and-safety)

---

## Core Team

### Responsibilities

The core team (Microsoft's OCTO MADE team) is responsible for:

- **Verification Review**: Reviewing and approving module verification requests (10-day SLA)
- **Namespace Management**: Managing reserved namespaces and approving exceptions
- **Policy Decisions**: Making final decisions on governance policies
- **Security Response**: Responding to security issues in verified modules
- **Registry Maintenance**: Maintaining registry infrastructure and automation
- **Dispute Resolution**: Resolving conflicts between module authors

### Team Composition

- Members from Microsoft's Office of the CTO (OCTO) MADE (Model, App Development & Extensibility) team
- Contact: [Create an issue](https://github.com/microsoft/amplifier-module-registry/issues) with `@microsoft/amplifier-core-team` tag

### Decision Authority

- **Verification decisions**: Requires 1 core team member approval
- **Policy changes**: Requires consensus of core team
- **Security actions**: Any core team member can take immediate action
- **Dispute resolution**: 2+ core team members required

---

## Module Verification

Verified modules receive a ✓ Verified badge and placement in `registry/verified/`, indicating they meet higher quality and trust standards.

### Verification Criteria

To be considered for verification, a module must meet ALL of the following:

#### 1. Product Quality

**Product Definition**:
- Clear definition of target audience
- Well-defined problem statement
- Documented solution approach
- **NOT required**: Production usage evidence (modules can be verified before widespread adoption)

**Documentation**:
- Comprehensive README with usage examples
- API documentation for all public interfaces
- Configuration options documented
- Troubleshooting guide

**Code Quality**:
- Clean, readable, well-structured code
- Follows Python best practices (PEP 8)
- Proper error handling
- No obvious security vulnerabilities

#### 2. Testing

- Unit tests with >70% coverage
- Integration tests for core functionality
- CI/CD pipeline with automated testing
- Tests pass consistently

#### 3. Maintenance

- Active maintainer(s) with GitHub presence
- Responsive to issues (< 7 day response time)
- Regular updates and bug fixes
- Semantic versioning followed correctly

#### 4. Security

- No known security vulnerabilities
- Dependencies are up-to-date
- Security best practices followed
- Clear security disclosure process

#### 5. Compatibility

- Works with current amplifier-foundation version
- Foundation version constraints clearly specified
- Breaking changes documented

### Verification Process

#### Step 1: Submission (Module Author)

1. Module must already be published in `registry/modules/`
2. Module must be live for at least 14 days
3. Create a verification request issue using the template
4. Provide:
   - **Audience**: Who will use this module?
   - **Problem**: What problem does it solve?
   - **Solution**: How does it solve the problem?
   - Links to documentation, tests, and repository

#### Step 2: Initial Review (Automated)

- CI checks all verification criteria automatically
- Generates compliance report
- Timeline: Immediate

#### Step 3: Team Review (Core Team - 10 Day SLA)

- Core team member reviews:
  - Product definition and documentation
  - Code quality and architecture
  - Test coverage and reliability
  - Security considerations
  - Community feedback (if any)
- **Service Level Agreement**: Review completed within 10 business days
- Reviewer may request changes or clarifications

#### Step 4: Decision

**Approved**:
- Module moved to `registry/verified/`
- Verification badge applied
- Announced in releases

**Rejected**:
- Feedback provided with specific improvements needed
- Can resubmit after 30 days with improvements

**Deferred**:
- Requires more information or time
- Author can provide additional context

### Verification Benefits

- ✓ Verified badge in all listings
- Higher visibility in search results
- Listed separately in `registry/verified/`
- Core team support for issues
- Promoted in official documentation

### Ongoing Requirements

Verified modules must maintain standards:

- **Response Time**: Issues acknowledged within 7 days
- **Security**: Critical vulnerabilities patched within 48 hours
- **Updates**: Compatible with new foundation versions within 30 days
- **Testing**: Maintain test coverage >70%

### Verification Revocation

Verification can be revoked in the following scenarios:

#### Immediate Revocation (Security/Safety)

1. **Critical Security Vulnerability**: Unpatched critical CVE >7 days after disclosure
2. **Malicious Behavior**: Evidence of intentional harm (data exfiltration, backdoors, etc.)
3. **License Violation**: Violates open source licenses
4. **Code of Conduct Violation**: Maintainer engages in harassment or abuse

**Process**: Core team member can revoke immediately, notify author

#### Revocation with Warning (Quality/Maintenance)

1. **Abandonment**: No maintainer response >60 days to critical issues
2. **Breaking Compatibility**: Repeatedly breaks compatibility without notice
3. **Test Failures**: Sustained test failures >30 days
4. **Documentation Rot**: Documentation severely outdated or misleading

**Process**:
- Warning issued with 30-day remediation period
- If not addressed, verification revoked
- Author can reapply after fixes

#### Voluntary Revocation

Authors can request verification removal at any time (e.g., no longer maintaining to verified standards)

### Revocation Appeals

- Author can appeal within 14 days
- Provide evidence that issue has been resolved
- Core team reviews appeal within 10 business days
- Decision is final

---

## Namespace Management

### Reserved Namespaces

The following prefixes are reserved for official Microsoft/core team use:

- `amplifier-*`, `amp-*`
- `microsoft-*`, `msft-*`
- `azure-*`
- `official-*`, `core-*`, `foundation-*`

### Namespace Rules

1. **First-Come, First-Served**: Non-reserved namespaces claimed by first module using the prefix
2. **Namespace Ownership**: Prefix owner (by `author.github`) has priority for related modules
3. **Generic Names Discouraged**: Avoid overly generic names like `helper`, `utils`, `tools`
4. **Descriptive Names Preferred**: Use clear, specific names like `code-reviewer`, `github-integration`

### Requesting Reserved Namespace Exception

To use a reserved namespace:

1. Open an issue: "Reserved Namespace Request: [namespace]-[module-name]"
2. Provide:
   - Justification for using reserved namespace
   - Your organization/affiliation
   - Module purpose and scope
3. Core team reviews within 14 days
4. Approval requires consensus (2+ core team members)

Exceptions typically granted for:
- Microsoft teams/partners
- Official integrations with Microsoft services
- Extensions to core amplifier functionality

### Namespace Disputes

If two authors claim the same namespace:

1. First published module has priority
2. If truly ambiguous, core team arbitrates based on:
   - Module quality and maintenance
   - Community adoption
   - Clarity of naming
3. Decision final, losing party must rename within 30 days

---

## Module Lifecycle

### Active Status

- Module is maintained and functional
- Default status for new modules
- Listed in registry and searchable

### Deprecated Status

Set by author when:
- Better alternative exists
- Planning to sunset the module
- No longer recommended for new projects

**Requirements**:
- Update manifest: `status: deprecated`
- Add deprecation notice to README
- Specify recommended alternative (if any)
- Continue critical bug fixes for 90 days

### Broken Status

Set by registry automation when:
- Incompatible with current foundation version
- Installation fails consistently
- Critical tests failing

**Process**:
- Automated compatibility checker detects issue
- GitHub issue opened tagging author
- Module marked `status: broken`
- Listed with warning in registry
- Author has 30 days to fix before archival

### Archived Status

Set when:
- Module unmaintained >180 days
- Author requests archival
- Broken status not resolved in 30 days

**Effect**:
- Moved to `registry/archived/`
- No longer listed in search
- Installation blocked (warning message)
- Can be restored if new maintainer takes over

### Ownership Transfer

To transfer module ownership:

1. Current owner opens issue: "Ownership Transfer: [module-name]"
2. Provide new owner's GitHub username
3. New owner confirms acceptance
4. Core team updates manifest `author` field
5. New owner added to repository permissions

### Module Removal

Modules can only be removed by:

1. **Author Request**: Author requests permanent deletion
2. **Policy Violation**: Repeated Code of Conduct violations
3. **Legal Requirement**: DMCA, court order, etc.

**Process**:
- Core team reviews request
- 30-day notice period (unless legal/safety issue)
- Dependents notified if possible
- Module removed from registry
- Entry preserved in archive for audit

---

## Breaking Changes

### Foundation Breaking Changes

When `amplifier-foundation` releases a breaking version (e.g., 1.0 → 2.0):

#### Notification Process

1. **Pre-release (60 days before)**:
   - Core team announces upcoming breaking changes
   - Migration guide published
   - Module authors notified via GitHub issue

2. **Release Day**:
   - Automated compatibility checker runs
   - Incompatible modules flagged as "needs-update"
   - Authors notified with specific failures

3. **Grace Period (30 days)**:
   - Modules remain active with warning
   - Authors update and test against new version
   - Core team provides support

4. **Post-Grace**:
   - Still-incompatible modules marked `broken`
   - Installation blocked with error message
   - Can be fixed and restored anytime

### Module Breaking Changes

Module authors introducing breaking changes:

1. **Increment major version** (e.g., 1.5.0 → 2.0.0)
2. **Document in CHANGELOG**
3. **Provide migration guide**
4. **Keep prior major version available** (via versions/)

Best practice: Support previous major version for 90 days minimum

---

## Dispute Resolution

### Types of Disputes

1. **Namespace conflicts** (resolved per Namespace Management section)
2. **Verification decisions** (appeal process defined above)
3. **Code of Conduct violations** (see below)
4. **Technical disagreements** (core team mediates)

### Process

1. **Open Issue**: Create issue with "Dispute:" prefix
2. **Present Case**: Both parties provide evidence and arguments
3. **Core Team Review**: 2+ team members review within 14 days
4. **Decision**: Made by majority vote, documented publicly
5. **Appeal**: Can appeal within 7 days with new evidence
6. **Final Decision**: After appeal review, decision is final

### Code of Conduct Violations

We follow the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

**Reporting**: Email security@microsoft.com or open confidential issue

**Consequences**:
- Warning for first minor offense
- Temporary suspension for repeated or moderate offenses
- Permanent ban for severe violations

---

## Security and Safety

### Security Vulnerability Disclosure

**For verified modules**:
- Report to module author privately first
- If no response in 7 days, report to core team via security@microsoft.com
- Core team will coordinate disclosure

**For community modules**:
- Report to author
- Optionally notify core team for awareness
- No SLA guarantee from core team

### Security Response SLA (Verified Modules Only)

- **Critical** (CVSS 9.0-10.0): 48 hours
- **High** (CVSS 7.0-8.9): 7 days
- **Medium** (CVSS 4.0-6.9): 30 days
- **Low** (CVSS 0.1-3.9): Best effort

### Safety Checks

Automated checks scan for:
- Known vulnerable dependencies
- Suspicious code patterns
- Overly broad permissions
- Network access to unexpected domains

Modules failing safety checks are flagged for manual review.

---

## Amendments

This governance document may be updated by the core team. Major changes will be announced with 30 days notice and community feedback period.

**Last Updated**: 2025-12-16
**Version**: 1.0.0
