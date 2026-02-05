# CodeScribe Development and Contribution Guidelines

This document outlines the official development processes, workflow standards, and collaboration rules for CodeScribe. As a developer on this project, you are required to adhere strictly to these guidelines. These standards ensure codebase stability, tracking clarity, and seamless integration of new features.

---

## 1. Feature Development and Branching Strategy

All development work must follow a structured feature-branch workflow. Direct modification of the main branch is strictly prohibited.

### 1.1 Branch Naming Conventions
Every branch must be linked to a specific task or issue and must use the following naming patterns:
* **Feature Branches**: `feature/short-description` (for new features or enhancements)
* **Bugfix Branches**: `bugfix/issue-id-short-description` (for resolving tracked bugs)
* **Hotfix Branches**: `hotfix/short-description` (for critical, urgent production issues)
* **Documentation Branches**: `docs/short-description` (for pure documentation updates)

*Example branch names:*
* `feature/ast-parser-python`
* `bugfix/102-fix-recursion-limit`
* `docs/update-installation-guide`

### 1.2 Development Lifecycle
1. **Branch Origin**: Always create your feature or bugfix branch from the latest state of the `main` branch.
2. **Synchronization**: Keep your branch up to date with the latest changes on `main` using rebase to avoid merge conflicts later:
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/your-branch-name
   git rebase main
   ```
3. **Local Validation**: Before pushing any changes, you must run all local tests and linter suites. Code that breaks local environments must not be pushed.

---

## 2. Issue Management and Tracking

We use issues to track all tasks, feature requests, and bugs. No code changes should be made without an associated, approved issue.

### 2.1 Creating Issues
When creating an issue, you must provide comprehensive details to ensure any developer can understand and act on it:
* **Clear Title**: Summarize the problem or feature concisely.
* **Detailed Description**: Explain what needs to be built or fixed.
* **Acceptance Criteria**: Provide a bulleted list of requirements that must be met for the issue to be considered complete.
* **Context/Environment**: For bug reports, specify the OS, Python version, dependency state, and provide steps to reproduce the issue along with actual vs. expected behavior.

### 2.2 Lifecycle of an Issue
1. **Triaged**: The Project Head reviews, approves, and assigns the issue.
2. **In Progress**: The assigned developer moves the issue to "In Progress" and starts development in a dedicated branch.
3. **In Review**: The developer creates a Pull Request (PR) and links it to the issue using Git keywords (e.g., `Closes #12`).
4. **Closed**: Once the PR is merged, the issue is closed automatically.

---

## 3. Commit and Push Policies

We maintain a clean, readable, and linear commit history.

### 3.1 Direct Push Restrictions
* **No Direct Pushes to Main**: Direct pushes to the `main` branch are blocked. All code must enter `main` through an approved Pull Request.
* **Branch Pushing**: You may push your feature branches to the remote repository (`origin`) frequently to ensure backups and remote collaboration.

### 3.2 Commit Message Standards
Commit messages must be clear, concise, and professional. We use the imperative style:
* **Style**: `Action: Short description in present tense`
* **Format**:
  * Good: `impl: add python ast parsing logic`
  * Good: `fix: resolve memory leak in semantic analyzer`
  * Good: `docs: update contributing guidelines`
  * Bad: `fixed the bug in parser`
  * Bad: `Added new cli file`
* **Emoji Restriction**: Do not use emojis in commit messages or pull request descriptions.
* **Atomic Commits**: Keep commits small and focused on a single change. Avoid committing unrelated modifications together.

---

## 4. Pull Request (PR) Workflow and Code Review

The Pull Request is our primary tool for maintaining code quality.

### 4.1 PR Requirements
Before submitting a PR for review, ensure you have completed the following checklist:
1. **Self-Review**: Review your own code diff to remove any debugging logs, temporary code, or commented-out blocks.
2. **Linked Issue**: Ensure the PR description references the issue it resolves (e.g., `Resolves #45`).
3. **Testing**: All automated tests must pass successfully. If new code is added, corresponding unit or integration tests must be written to cover it.
4. **Documentation**: Update code docstrings and relevant external docs (`README.md` or files in `docs/`) to reflect the changes.

### 4.2 Code Review Protocol
* **Reviewers**: Every PR requires a minimum of one peer review. The Project Head reserves final approval rights before any merge.
* **Addressing Feedback**: Address reviewer feedback promptly. If changes are requested, push new commits to your existing branch; they will automatically update the PR.
* **Merging Strategy**: We utilize a **Squash and Merge** strategy. This condenses all commits from your feature branch into a single, clean commit on `main`.

---

## 5. Coding Standards and Codebase Quality

As a team, we maintain high standards of code hygiene:
* **Formatting**: We adhere to PEP 8 standards for all Python code. Run `black` or `flake8` to format code before committing.
* **Docstrings**: All new classes, methods, and functions must have descriptive docstrings following the Google Style Python Docstrings convention.
* **Type Hinting**: CodeScribe utilizes modern Python type hinting. Ensure all function signatures specify argument and return types.
