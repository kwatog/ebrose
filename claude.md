# Claude Code CLI Guide for Ebrose

> **📖 Main Documentation:** See [`agents.md`](./agents.md) for complete AI assistant guidelines including:
> - Git commit guidelines and message format
> - Code style guidelines (Python/TypeScript/Vue)
> - Testing requirements and patterns
> - Security guidelines
> - Database change procedures
> - Common development patterns
> - Container image management
> - Kubernetes deployment procedures
> - Helpful commands

## Claude Code-Specific Notes

When working with this project using Claude Code CLI, follow all guidelines in [`agents.md`](./agents.md) and note these Claude Code-specific behaviors:

### Autonomous Task Execution

Claude Code is optimized for:
- Code exploration and analysis
- Feature implementation with plan mode
- Debugging and troubleshooting
- Automated testing and fixes
- Deployment operations

### Task Management

Claude Code uses a built-in todo list to track progress. Trust the process:
- Complex tasks are automatically broken down
- Progress is tracked in real-time
- Items are marked complete as work finishes

### Plan Mode

For complex implementations, Claude Code will:
1. Enter plan mode automatically
2. Explore the codebase thoroughly
3. Design the implementation approach
4. Request your approval before coding
5. Execute the approved plan

This prevents wasted effort and ensures alignment.

### Project-Specific Reminders

- **Container Runtime**: This system uses **Podman**, not Docker
- **Worker Node Access**: Use IP addresses (192.168.18.66, 192.168.18.68), not hostnames
- **Containerd Permissions**: User must be in `containerd` group and start new shell session
- **Commit Format**: No AI attribution footers (project policy)

---

**For all other guidelines, workflows, and commands, see [`agents.md`](./agents.md)**
