---
name: agent-creator
description: Guide for creating effective subagents. Use when users want to create a new subagent (or update an existing subagent) that handles specialized tasks with isolated context, specific tool access, and custom system prompts.
---

# Agent Creator Guide

## About Subagents

Subagents are isolated Claude instances that handle specific tasks with their own context, tools, and system prompts. They run via the `Task` tool and return results to the parent conversation.

### When to Use Subagents vs Skills

| Use Subagents When | Use Skills When |
|-------------------|-----------------|
| Task needs isolated context | Extending main agent's knowledge |
| Restricting tool access for safety | Adding workflows/procedures |
| Delegating to run in background | User-invocable commands |
| Task benefits from different model | No context isolation needed |

## Core Principles

1. **Single Responsibility** - Each agent should do one thing well
2. **Minimal Tool Access** - Only grant tools the agent actually needs
3. **Clear System Prompts** - Be specific about behavior and constraints
4. **Context Preservation** - Design prompts so agents have what they need

## Anatomy of a Subagent

Agent files are Markdown with YAML frontmatter:

```markdown
---
name: my-agent
description: When Claude should delegate to this agent
tools: Read, Grep, Glob
model: sonnet
---

You are a specialized agent that...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase with hyphens, max 64 chars |
| `description` | Yes | When to use this agent (max 1024 chars) |
| `tools` | No | Comma-separated tool list (default: all) |
| `disallowedTools` | No | Tools to explicitly deny |
| `model` | No | `sonnet`, `opus`, `haiku`, or omit to inherit |
| `permissionMode` | No | Permission handling mode |
| `skills` | No | Skills available to this agent |
| `hooks` | No | Event hooks for the agent |

### System Prompt (Body)

The markdown body after frontmatter becomes the agent's system prompt. Write it as instructions directly addressing the agent.

## Agent Creation Process

### Step 1: Understand the Use Case

Ask clarifying questions:
- What specific task will this agent handle?
- Does it need to modify files or just read?
- Should it run with a lighter/heavier model?
- What safety constraints are needed?

### Step 2: Plan Tool Permissions

Refer to `references/tool-permissions.md` for:
- Available tools and their purposes
- Common tool combinations by agent type
- When to use `tools` vs `disallowedTools`

### Step 3: Initialize the Agent

Run the initialization script:

```bash
python .claude/skills/agent-creator/scripts/init_agent.py <agent-name> --scope project
```

Options:
- `--scope project` - Create in `.claude/agents/` (default)
- `--scope user` - Create in `~/.claude/agents/`
- `--path <path>` - Custom location

### Step 4: Write the System Prompt

Edit the generated file to add:
- Clear role definition
- Specific behavioral instructions
- Output format expectations
- Any constraints or guardrails

### Step 5: Validate the Agent

Run validation to check for errors:

```bash
python .claude/skills/agent-creator/scripts/validate_agent.py .claude/agents/<agent-name>.md
```

### Step 6: Iterate Based on Usage

Test the agent by invoking it via `/agents` or the Task tool. Refine the system prompt based on actual behavior.

## References

- `references/tool-permissions.md` - Complete tool list and permission patterns
- `references/agent-patterns.md` - Common agent patterns and examples
