#!/usr/bin/env -S uv run
"""Fork a new terminal window with a command."""

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


def get_python_command() -> List[str]:
    """Get the python command with uv if available."""
    if shutil.which('uv'):
        return ['uv', 'run', 'python']
    return ['python3']


def fork_terminal(command: str) -> str:
    """Open a new Terminal window and run the specified command."""
    system = platform.system()
    cwd = os.getcwd()

    if system == "Darwin":  # macOS
        # Build shell command - use single quotes for cd to avoid escaping issues
        # Then escape everything for AppleScript
        shell_command = f"cd '{cwd}' && {command}"
        # Escape for AppleScript: backslashes first, then quotes
        escaped_shell_command = shell_command.replace("\\", "\\\\").replace('"', '\\"')

        try:
            result = subprocess.run(
                ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_shell_command}"'],
                capture_output=True,
                text=True,
            )
            output = f"stdout: {result.stdout.strip()}\nstderr: {result.stderr.strip()}\nreturn_code: {result.returncode}"
            return output
        except Exception as e:
            return f"Error: {str(e)}"

    elif system == "Windows":
        # Use /d flag to change drives if necessary
        full_command = f'cd /d "{cwd}" && {command}'
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/c", full_command], shell=True)
        return "Windows terminal launched"

    else:  # Linux and others
        raise NotImplementedError(f"Platform {system} not supported")


def create_agent_context_file(
    agent_id: str,
    role: str,
    task: Optional[Dict[str, Any]] = None,
    checkpoint: Optional[Dict[str, Any]] = None,
    agents_dir: str = ".claude/agents"
) -> str:
    """
    Create a combined context file for an agent.

    Combines:
    - Role definition from .claude/agents/roles/{role}.md
    - Project context from .claude/agents/project-context/*.md
    - Current task assignment
    - Checkpoint state (if resuming)

    Args:
        agent_id: Agent identifier
        role: Agent role (frontend, backend, devops, qa, architect)
        task: Task assignment dict (task_id, description, etc.)
        checkpoint: Previous checkpoint data (if resuming)
        agents_dir: Path to agents directory

    Returns:
        Path to created context file
    """
    agents_path = Path(agents_dir)

    # Read role definition
    role_file = agents_path / "roles" / f"{role}.md"
    if role_file.exists():
        with open(role_file) as f:
            role_content = f.read()
    else:
        role_content = f"# {role.title()} Agent\n\nRole definition not found."

    # Read project context files
    project_context = []
    context_dir = agents_path / "project-context"
    if context_dir.exists():
        for ctx_file in sorted(context_dir.glob("*.md")):
            try:
                with open(ctx_file) as f:
                    content = f.read()
                    project_context.append(f"## {ctx_file.name}\n\n{content}")
            except Exception:
                pass

    # Read shared knowledge (API contracts, etc.)
    shared_knowledge = []
    shared_dir = Path(".agent-comm/shared-knowledge")
    if shared_dir.exists():
        # API contracts
        api_contracts_dir = shared_dir / "api-contracts"
        if api_contracts_dir.exists():
            for contract_file in api_contracts_dir.glob("*.yaml"):
                try:
                    with open(contract_file) as f:
                        shared_knowledge.append(
                            f"### API Contract: {contract_file.stem}\n```yaml\n{f.read()}\n```"
                        )
                except Exception:
                    pass

        # Design decisions
        decisions_dir = shared_dir / "design-decisions"
        if decisions_dir.exists():
            for decision_file in decisions_dir.glob("*.md"):
                try:
                    with open(decision_file) as f:
                        shared_knowledge.append(
                            f"### Design Decision: {decision_file.stem}\n{f.read()}"
                        )
                except Exception:
                    pass

    # Build combined context
    context_parts = [
        f"# Agent Context for {agent_id}",
        f"Generated: {datetime.utcnow().isoformat()}",
        "",
        "# Your Role",
        role_content,
        "",
        "# Project Context",
        *project_context,
    ]

    if shared_knowledge:
        context_parts.extend([
            "",
            "# Shared Knowledge",
            *shared_knowledge
        ])

    if task:
        context_parts.extend([
            "",
            "# Current Task",
            f"**Task ID**: {task.get('task_id', 'N/A')}",
            f"**Description**: {task.get('description', 'N/A')}",
            f"**Priority**: {task.get('priority', 'N/A')}",
            "",
            f"**Expected Outputs**: {task.get('metadata', {}).get('expected_files', 'Not specified')}",
        ])

        if task.get('dependencies'):
            context_parts.extend([
                "",
                f"**Dependencies**: {', '.join(task['dependencies'])}",
                "(These tasks must complete before you can start)"
            ])

    if checkpoint:
        context_parts.extend([
            "",
            "# Resuming from Checkpoint",
            f"You are resuming work that was previously started.",
            "",
            "## Previous Progress",
            f"- **Last checkpoint**: {checkpoint.get('checkpoint_time', 'Unknown')}",
            f"- **Phase**: {checkpoint.get('state', {}).get('phase', 'Unknown')}",
        ])

        state = checkpoint.get('state', {})
        if 'completed_steps' in state:
            context_parts.append("\n**Completed steps**:")
            for step in state['completed_steps']:
                context_parts.append(f"- ✅ {step}")

        if 'next_steps' in state:
            context_parts.append("\n**Next steps**:")
            for step in state['next_steps']:
                context_parts.append(f"- ⏭️  {step}")

        wip = checkpoint.get('work_in_progress', {})
        if wip.get('files_modified'):
            context_parts.append("\n**Files in progress**:")
            for file in wip['files_modified']:
                context_parts.append(f"- {file}")

    # Write to temp file
    context_content = "\n".join(context_parts)

    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix=f'-{agent_id}.md',
        prefix='agent-context-',
        delete=False
    )
    temp_file.write(context_content)
    temp_file.close()

    return temp_file.name


def fork_agent(
    agent_id: str,
    role: str,
    task: Optional[Dict[str, Any]] = None,
    checkpoint: Optional[Dict[str, Any]] = None,
    comm_dir: str = ".agent-comm",
    agents_dir: str = ".claude/agents"
) -> str:
    """
    Fork a new agent terminal with full context.

    Args:
        agent_id: Unique agent identifier (e.g., "frontend-001")
        role: Agent role (frontend, backend, devops, qa, architect)
        task: Task assignment dict
        checkpoint: Previous checkpoint (if resuming)
        comm_dir: Communication directory
        agents_dir: Agents configuration directory

    Returns:
        Output from fork_terminal

    Example:
        >>> fork_agent(
        ...     agent_id="frontend-001",
        ...     role="frontend",
        ...     task={"task_id": "task-042", "description": "Build login form"}
        ... )
    """
    # Create completion directory
    completion_dir = Path(comm_dir) / "completion"
    completion_dir.mkdir(parents=True, exist_ok=True)

    # Create context file
    context_file = create_agent_context_file(
        agent_id=agent_id,
        role=role,
        task=task,
        checkpoint=checkpoint,
        agents_dir=agents_dir
    )

    # Build command to run agent worker
    # Note: Assuming agent_worker.py is in same directory
    worker_script = Path(__file__).parent / "agent_worker.py"

    command_parts = get_python_command() + [
        str(worker_script),
        f"--agent-id {agent_id}",
        f"--role {role}",
        f"--context-file {context_file}",
        f"--comm-dir {comm_dir}"
    ]

    if task and task.get('task_id'):
        command_parts.append(f"--task-id {task['task_id']}")

    command = " ".join(command_parts)

    # Fork terminal with agent worker
    return fork_terminal(command)


def fork_agent_with_handover(
    agent_id: str,
    role: str,
    previous_agent_id: str,
    comm_dir: str = ".agent-comm"
) -> str:
    """
    Fork agent with checkpoint from crashed/stopped agent.

    Args:
        agent_id: New agent identifier
        role: Agent role
        previous_agent_id: Previous agent that crashed
        comm_dir: Communication directory

    Returns:
        Output from fork_terminal
    """
    from checkpoint_manager import CheckpointManager

    # Load previous agent's checkpoint
    checkpoint_mgr = CheckpointManager(f"{comm_dir}/checkpoints")
    checkpoint = checkpoint_mgr.load_latest_checkpoint(previous_agent_id)

    if not checkpoint:
        raise ValueError(f"No checkpoint found for {previous_agent_id}")

    # Extract task from checkpoint
    task = {
        "task_id": checkpoint.task_id,
        "description": checkpoint.work_in_progress.get('task_description', 'Unknown'),
    }

    # Fork new agent with checkpoint
    return fork_agent(
        agent_id=agent_id,
        role=role,
        task=task,
        checkpoint=checkpoint.to_dict(),
        comm_dir=comm_dir
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        output = fork_terminal(" ".join(sys.argv[1:]))
        print(output)
