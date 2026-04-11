# Tool Permissions Reference

## Available Tools

### File Operations
| Tool | Purpose | Risk Level |
|------|---------|------------|
| `Read` | Read file contents | Low |
| `Write` | Create/overwrite files | Medium |
| `Edit` | Modify existing files | Medium |
| `NotebookEdit` | Edit Jupyter notebooks | Medium |
| `Glob` | Find files by pattern | Low |
| `Grep` | Search file contents | Low |

### System Operations
| Tool | Purpose | Risk Level |
|------|---------|------------|
| `Bash` | Execute shell commands | High |

### Web Operations
| Tool | Purpose | Risk Level |
|------|---------|------------|
| `WebFetch` | Fetch URL content | Low |
| `WebSearch` | Search the web | Low |

### Task Management
| Tool | Purpose | Risk Level |
|------|---------|------------|
| `Task` | Launch subagents | Medium |
| `TaskOutput` | Get task results | Low |
| `TaskStop` | Stop running tasks | Low |

### Workflow Tools
| Tool | Purpose | Risk Level |
|------|---------|------------|
| `TaskCreate` | Create todo items | Low |
| `TaskGet` | Get task details | Low |
| `TaskUpdate` | Update tasks | Low |
| `TaskList` | List all tasks | Low |
| `Skill` | Invoke skills | Medium |
| `AskUserQuestion` | Prompt user | Low |
| `EnterPlanMode` | Start planning | Low |
| `ExitPlanMode` | Exit planning | Low |

## Common Tool Combinations

### Read-Only Agent
```yaml
tools: Read, Grep, Glob
```
Use for: Code reviewers, analyzers, documentation readers

### Research Agent
```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```
Use for: Documentation lookup, API research, fact-checking

### Code Modification Agent
```yaml
tools: Read, Grep, Glob, Write, Edit
```
Use for: Refactoring, code generation, file updates

### Full Development Agent
```yaml
tools: Read, Grep, Glob, Write, Edit, Bash
```
Use for: Build runners, test executors, deployment agents

### Exploration Agent
```yaml
tools: Read, Grep, Glob, Bash(ls*), Bash(git log*), Bash(git diff*)
```
Use for: Codebase exploration with limited safe commands

## Using `tools` vs `disallowedTools`

### Use `tools` (allowlist) when:
- Agent has a narrow, well-defined purpose
- You want explicit control over capabilities
- Security is a primary concern

### Use `disallowedTools` (blocklist) when:
- Agent needs most tools except a few
- You want to prevent specific dangerous operations
- Flexibility is more important than strict control

### Example: Block only dangerous tools
```yaml
disallowedTools: Bash, Write, Edit, Task
```

## Bash Command Restrictions

You can scope Bash access to specific commands:

```yaml
tools: Read, Grep, Glob, Bash(npm test*), Bash(npm run lint*)
```

This allows only `npm test` and `npm run lint` commands.

### Common restricted patterns:
- `Bash(git status*)` - Git status only
- `Bash(npm test*)` - Test execution only
- `Bash(python -m pytest*)` - Python tests only
- `Bash(ls*)` - Directory listing only
- `Bash(cat*)` - File viewing only (prefer Read tool)

## Security Considerations

1. **Principle of Least Privilege** - Only grant tools the agent actually needs
2. **Bash is powerful** - Consider command restrictions or avoid entirely
3. **Write/Edit can be destructive** - Use for agents that truly need file modification
4. **Task can spawn more agents** - Consider if recursive agent spawning is needed
5. **WebFetch/WebSearch** - Safe for most uses, but consider if external access is needed
