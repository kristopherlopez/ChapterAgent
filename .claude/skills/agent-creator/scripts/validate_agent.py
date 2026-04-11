#!/usr/bin/env python3
"""
Validate a Claude Code subagent definition file.

Usage:
    validate_agent.py <path-to-agent.md>

Example:
    validate_agent.py .claude/agents/code-reviewer.md
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


# Valid tools in Claude Code
VALID_TOOLS = {
    "Read", "Write", "Edit", "NotebookEdit",
    "Bash", "Glob", "Grep",
    "WebFetch", "WebSearch",
    "Task", "TaskOutput", "TaskStop",
    "AskUserQuestion", "Skill",
    "EnterPlanMode", "ExitPlanMode",
    "TaskCreate", "TaskGet", "TaskUpdate", "TaskList",
}

VALID_MODELS = {"sonnet", "opus", "haiku", "inherit"}

ALLOWED_FIELDS = {
    "name", "description", "tools", "disallowedTools",
    "model", "permissionMode", "skills", "hooks"
}

REQUIRED_FIELDS = {"name", "description"}


def parse_frontmatter(content: str) -> tuple[dict | None, str, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None, "File must start with YAML frontmatter (---)", ""

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Invalid frontmatter format (missing closing ---)", ""

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    if yaml:
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            if not isinstance(frontmatter, dict):
                return None, "Frontmatter must be a YAML mapping", ""
            return frontmatter, "", body
        except yaml.YAMLError as e:
            return None, f"Invalid YAML: {e}", ""
    else:
        # Basic parsing without PyYAML
        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                frontmatter[key] = value
        return frontmatter, "", body


def validate_name(name: str) -> list[str]:
    """Validate the name field."""
    errors = []

    if not name:
        errors.append("name is required")
        return errors

    if not isinstance(name, str):
        errors.append("name must be a string")
        return errors

    if len(name) > 64:
        errors.append(f"name must be 64 characters or less (got {len(name)})")

    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        errors.append("name must be lowercase letters, numbers, and hyphens, starting with a letter")

    if '--' in name:
        errors.append("name cannot contain consecutive hyphens")

    if name.endswith('-'):
        errors.append("name cannot end with a hyphen")

    return errors


def validate_description(description: str) -> list[str]:
    """Validate the description field."""
    errors = []

    if not description:
        errors.append("description is required")
        return errors

    if not isinstance(description, str):
        errors.append("description must be a string")
        return errors

    if len(description) > 1024:
        errors.append(f"description must be 1024 characters or less (got {len(description)})")

    if '<' in description or '>' in description:
        errors.append("description cannot contain angle brackets")

    return errors


def validate_tools(tools: str) -> list[str]:
    """Validate the tools field."""
    errors = []

    if not tools:
        return errors  # Optional field

    if not isinstance(tools, str):
        errors.append("tools must be a comma-separated string")
        return errors

    tool_list = [t.strip() for t in tools.split(",")]

    for tool in tool_list:
        # Handle wildcards like "Bash(*)"
        base_tool = tool.split("(")[0]
        if base_tool not in VALID_TOOLS:
            errors.append(f"Unknown tool: {tool}")

    return errors


def validate_model(model: str) -> list[str]:
    """Validate the model field."""
    errors = []

    if not model:
        return errors  # Optional field

    if not isinstance(model, str):
        errors.append("model must be a string")
        return errors

    if model not in VALID_MODELS:
        errors.append(f"Invalid model: {model}. Must be one of: {', '.join(sorted(VALID_MODELS))}")

    return errors


def validate_agent(path: Path) -> list[str]:
    """Validate an agent file and return list of errors."""
    errors = []

    # Check file exists
    if not path.exists():
        return [f"File not found: {path}"]

    if not path.is_file():
        return [f"Not a file: {path}"]

    # Read content
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Cannot read file: {e}"]

    # Parse frontmatter
    frontmatter, parse_error, body = parse_frontmatter(content)
    if parse_error:
        return [parse_error]

    # Check for unknown fields
    for field in frontmatter:
        if field not in ALLOWED_FIELDS:
            errors.append(f"Unknown field: {field}")

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Validate individual fields
    if "name" in frontmatter:
        errors.extend(validate_name(frontmatter["name"]))

    if "description" in frontmatter:
        errors.extend(validate_description(frontmatter["description"]))

    if "tools" in frontmatter:
        errors.extend(validate_tools(frontmatter["tools"]))

    if "disallowedTools" in frontmatter:
        errors.extend(validate_tools(frontmatter["disallowedTools"]))

    if "model" in frontmatter:
        errors.extend(validate_model(frontmatter["model"]))

    # Check body has content
    if not body:
        errors.append("Agent file has no system prompt (body content after frontmatter)")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Claude Code subagent definition"
    )
    parser.add_argument("path", help="Path to the agent .md file")

    args = parser.parse_args()
    path = Path(args.path)

    errors = validate_agent(path)

    if errors:
        print(f"Validation failed for {path}:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Validation passed: {path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
