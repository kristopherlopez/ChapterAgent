#!/usr/bin/env python3
"""
Initialize a new Claude Code subagent with template frontmatter.

Usage:
    init_agent.py <agent-name> --scope <project|user> [--path <custom-path>]

Examples:
    init_agent.py code-reviewer --scope project
    init_agent.py my-helper --scope user
    init_agent.py custom-agent --path ./agents/
"""

import argparse
import os
import re
import sys
from pathlib import Path


def validate_agent_name(name: str) -> tuple[bool, str]:
    """Validate agent name format."""
    if len(name) > 64:
        return False, "Agent name must be 64 characters or less"

    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        return False, "Agent name must be lowercase letters, numbers, and hyphens, starting with a letter"

    if '--' in name:
        return False, "Agent name cannot contain consecutive hyphens"

    if name.endswith('-'):
        return False, "Agent name cannot end with a hyphen"

    return True, ""


def get_agent_path(name: str, scope: str, custom_path: str | None) -> Path:
    """Determine the agent file path based on scope."""
    if custom_path:
        base = Path(custom_path)
    elif scope == "user":
        base = Path.home() / ".claude" / "agents"
    else:  # project scope
        base = Path.cwd() / ".claude" / "agents"

    return base / f"{name}.md"


def generate_template(name: str) -> str:
    """Generate the agent template content."""
    return f"""---
name: {name}
description: "[TODO: Describe when Claude should delegate to this agent]"
tools: Read, Grep, Glob
model: inherit
---

# {name.replace('-', ' ').title()} Agent

[TODO: Write the system prompt for this agent]

## Role

You are a specialized agent that [describe purpose].

## Instructions

1. [First instruction]
2. [Second instruction]
3. [Third instruction]

## Output Format

[Describe expected output format]

## Constraints

- [Any limitations or guardrails]
"""


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Claude Code subagent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s code-reviewer --scope project
  %(prog)s my-helper --scope user
  %(prog)s custom-agent --path ./agents/
        """
    )
    parser.add_argument("name", help="Agent name (lowercase, hyphens allowed)")
    parser.add_argument(
        "--scope",
        choices=["project", "user"],
        default="project",
        help="Where to create the agent (default: project)"
    )
    parser.add_argument(
        "--path",
        help="Custom path override (ignores --scope)"
    )

    args = parser.parse_args()

    # Validate name
    valid, error = validate_agent_name(args.name)
    if not valid:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    # Determine path
    agent_path = get_agent_path(args.name, args.scope, args.path)

    # Check if already exists
    if agent_path.exists():
        print(f"Error: Agent already exists at {agent_path}", file=sys.stderr)
        sys.exit(1)

    # Create parent directories
    agent_path.parent.mkdir(parents=True, exist_ok=True)

    # Write template
    content = generate_template(args.name)
    agent_path.write_text(content, encoding="utf-8")

    print(f"Created agent: {agent_path}")
    print()
    print("Next steps:")
    print(f"  1. Edit {agent_path} to customize the system prompt")
    print(f"  2. Run: python validate_agent.py {agent_path}")
    print("  3. Test with /agents or Task tool")


if __name__ == "__main__":
    main()
