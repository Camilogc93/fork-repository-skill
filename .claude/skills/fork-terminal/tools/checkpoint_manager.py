#!/usr/bin/env python3
"""
Checkpoint Manager for Agent Orchestration System

Handles saving, loading, and managing agent state checkpoints for crash recovery
and session persistence.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import gzip
import shutil


@dataclass
class CheckpointData:
    """Agent checkpoint data structure."""

    agent_id: str
    role: str
    task_id: str
    checkpoint_time: str
    state: Dict[str, Any] = field(default_factory=dict)
    work_in_progress: Dict[str, Any] = field(default_factory=dict)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    communication_log: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'CheckpointData':
        """Create from dictionary."""
        return cls(**data)


class CheckpointManager:
    """Manages agent checkpoint operations."""

    def __init__(self, checkpoint_dir: str = ".agent-comm/checkpoints"):
        """
        Initialize checkpoint manager.

        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.compression_enabled = True  # Enable compression for large checkpoints
        self.max_checkpoints_per_agent = 5  # Keep last N checkpoints

    def save_checkpoint(
        self,
        agent_id: str,
        checkpoint_data: CheckpointData
    ) -> str:
        """
        Save agent checkpoint atomically.

        Args:
            agent_id: Agent identifier
            checkpoint_data: Checkpoint data to save

        Returns:
            Path to saved checkpoint file

        Raises:
            ValueError: If checkpoint data is invalid
            IOError: If checkpoint cannot be saved
        """
        # Validate checkpoint data
        if not self.validate_checkpoint(checkpoint_data):
            raise ValueError(f"Invalid checkpoint data for agent {agent_id}")

        # Generate checkpoint filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
        checkpoint_file = self.checkpoint_dir / f"{agent_id}-{timestamp}.json"

        # Use atomic write: write to temp file, then rename
        temp_file = checkpoint_file.with_suffix(".tmp")

        try:
            # Convert to JSON
            checkpoint_json = json.dumps(
                checkpoint_data.to_dict(),
                indent=2,
                default=str  # Handle datetime and other non-serializable types
            )

            # Write to temp file
            if self.compression_enabled and len(checkpoint_json) > 10000:
                # Compress large checkpoints
                with gzip.open(temp_file.with_suffix(".json.gz"), 'wt', encoding='utf-8') as f:
                    f.write(checkpoint_json)
                checkpoint_file = checkpoint_file.with_suffix(".json.gz")
                temp_file = temp_file.with_suffix(".json.gz")
            else:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(checkpoint_json)

            # Atomic rename
            temp_file.replace(checkpoint_file)

            # Create/update "latest" symlink for easy access
            latest_link = self.checkpoint_dir / f"{agent_id}-latest.json"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()

            # On Windows, copy instead of symlink (symlinks require admin)
            if os.name == 'nt':
                shutil.copy2(checkpoint_file, latest_link)
            else:
                latest_link.symlink_to(checkpoint_file.name)

            # Cleanup old checkpoints
            self._cleanup_old_checkpoints(agent_id)

            return str(checkpoint_file)

        except Exception as e:
            # Cleanup temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise IOError(f"Failed to save checkpoint for {agent_id}: {str(e)}")

    def load_checkpoint(self, checkpoint_file: str) -> Optional[CheckpointData]:
        """
        Load checkpoint from file.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            CheckpointData if successful, None if file doesn't exist

        Raises:
            ValueError: If checkpoint file is corrupted
        """
        checkpoint_path = Path(checkpoint_file)

        if not checkpoint_path.exists():
            return None

        try:
            # Detect if compressed
            if checkpoint_path.suffix == '.gz':
                with gzip.open(checkpoint_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

            # Validate before returning
            checkpoint = CheckpointData.from_dict(data)
            if not self.validate_checkpoint(checkpoint):
                raise ValueError("Checkpoint validation failed")

            return checkpoint

        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted checkpoint file {checkpoint_file}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load checkpoint {checkpoint_file}: {str(e)}")

    def load_latest_checkpoint(self, agent_id: str) -> Optional[CheckpointData]:
        """
        Load the most recent checkpoint for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Most recent CheckpointData or None if no checkpoints exist
        """
        # Try to load from "latest" link first
        latest_link = self.checkpoint_dir / f"{agent_id}-latest.json"
        if latest_link.exists():
            return self.load_checkpoint(str(latest_link))

        # Fallback: find most recent checkpoint file
        checkpoints = self.list_checkpoints(agent_id)
        if not checkpoints:
            return None

        # Checkpoints are sorted by timestamp (newest first)
        return self.load_checkpoint(checkpoints[0])

    def list_checkpoints(self, agent_id: str) -> List[str]:
        """
        List all checkpoint files for an agent, sorted by timestamp (newest first).

        Args:
            agent_id: Agent identifier

        Returns:
            List of checkpoint file paths
        """
        # Find all checkpoint files for this agent
        pattern = f"{agent_id}-*.json"
        gz_pattern = f"{agent_id}-*.json.gz"

        checkpoints = []
        checkpoints.extend(self.checkpoint_dir.glob(pattern))
        checkpoints.extend(self.checkpoint_dir.glob(gz_pattern))

        # Filter out "latest" links
        checkpoints = [
            cp for cp in checkpoints
            if not cp.name.endswith('-latest.json')
        ]

        # Sort by modification time (newest first)
        checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return [str(cp) for cp in checkpoints]

    def validate_checkpoint(self, checkpoint_data: CheckpointData) -> bool:
        """
        Validate checkpoint data structure.

        Args:
            checkpoint_data: Checkpoint to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not checkpoint_data.agent_id:
                return False
            if not checkpoint_data.role:
                return False
            if not checkpoint_data.task_id:
                return False
            if not checkpoint_data.checkpoint_time:
                return False

            # Validate state structure
            if not isinstance(checkpoint_data.state, dict):
                return False

            # Validate work_in_progress structure
            if not isinstance(checkpoint_data.work_in_progress, dict):
                return False

            # Validate context_snapshot structure
            if not isinstance(checkpoint_data.context_snapshot, dict):
                return False

            # Validate communication_log structure
            if not isinstance(checkpoint_data.communication_log, list):
                return False

            return True

        except Exception:
            return False

    def delete_checkpoint(self, checkpoint_file: str) -> bool:
        """
        Delete a checkpoint file.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            True if deleted, False if file doesn't exist
        """
        checkpoint_path = Path(checkpoint_file)

        if not checkpoint_path.exists():
            return False

        try:
            checkpoint_path.unlink()
            return True
        except Exception:
            return False

    def _cleanup_old_checkpoints(self, agent_id: str):
        """
        Remove old checkpoints, keeping only the most recent N.

        Args:
            agent_id: Agent identifier
        """
        checkpoints = self.list_checkpoints(agent_id)

        # Keep only max_checkpoints_per_agent
        if len(checkpoints) > self.max_checkpoints_per_agent:
            old_checkpoints = checkpoints[self.max_checkpoints_per_agent:]
            for checkpoint_file in old_checkpoints:
                self.delete_checkpoint(checkpoint_file)

    def cleanup_all_checkpoints(self, agent_id: str):
        """
        Delete all checkpoints for an agent.

        Args:
            agent_id: Agent identifier
        """
        checkpoints = self.list_checkpoints(agent_id)
        for checkpoint_file in checkpoints:
            self.delete_checkpoint(checkpoint_file)

        # Also remove "latest" link
        latest_link = self.checkpoint_dir / f"{agent_id}-latest.json"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()

    def get_checkpoint_size(self, checkpoint_file: str) -> int:
        """
        Get checkpoint file size in bytes.

        Args:
            checkpoint_file: Path to checkpoint file

        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        checkpoint_path = Path(checkpoint_file)

        if not checkpoint_path.exists():
            return 0

        return checkpoint_path.stat().st_size

    def create_checkpoint_from_dict(
        self,
        agent_id: str,
        role: str,
        task_id: str,
        state: Optional[Dict] = None,
        work_in_progress: Optional[Dict] = None,
        context_snapshot: Optional[Dict] = None,
        communication_log: Optional[List] = None
    ) -> CheckpointData:
        """
        Create a checkpoint data object.

        Args:
            agent_id: Agent identifier
            role: Agent role
            task_id: Current task ID
            state: Agent state
            work_in_progress: Work in progress data
            context_snapshot: Context snapshot
            communication_log: Communication history

        Returns:
            CheckpointData object
        """
        return CheckpointData(
            agent_id=agent_id,
            role=role,
            task_id=task_id,
            checkpoint_time=datetime.utcnow().isoformat(),
            state=state or {},
            work_in_progress=work_in_progress or {},
            context_snapshot=context_snapshot or {},
            communication_log=communication_log or []
        )


# Convenience functions for common operations
def save_agent_checkpoint(
    agent_id: str,
    role: str,
    task_id: str,
    state: Dict,
    work_in_progress: Dict,
    context_snapshot: Dict,
    communication_log: List,
    checkpoint_dir: str = ".agent-comm/checkpoints"
) -> str:
    """
    Convenience function to save agent checkpoint.

    Args:
        agent_id: Agent identifier
        role: Agent role
        task_id: Current task ID
        state: Agent state
        work_in_progress: Work in progress
        context_snapshot: Context snapshot
        communication_log: Communication log
        checkpoint_dir: Checkpoint directory

    Returns:
        Path to saved checkpoint
    """
    manager = CheckpointManager(checkpoint_dir)
    checkpoint = manager.create_checkpoint_from_dict(
        agent_id=agent_id,
        role=role,
        task_id=task_id,
        state=state,
        work_in_progress=work_in_progress,
        context_snapshot=context_snapshot,
        communication_log=communication_log
    )
    return manager.save_checkpoint(agent_id, checkpoint)


def load_agent_checkpoint(
    agent_id: str,
    checkpoint_dir: str = ".agent-comm/checkpoints"
) -> Optional[CheckpointData]:
    """
    Convenience function to load latest agent checkpoint.

    Args:
        agent_id: Agent identifier
        checkpoint_dir: Checkpoint directory

    Returns:
        CheckpointData or None
    """
    manager = CheckpointManager(checkpoint_dir)
    return manager.load_latest_checkpoint(agent_id)


if __name__ == "__main__":
    # Example usage
    print("Checkpoint Manager - Example Usage")
    print("=" * 50)

    # Create checkpoint manager
    manager = CheckpointManager()

    # Create example checkpoint
    checkpoint = manager.create_checkpoint_from_dict(
        agent_id="frontend-001",
        role="frontend",
        task_id="task-042",
        state={
            "current_step": 3,
            "total_steps": 5,
            "completed_steps": [
                "Created component skeleton",
                "Added state management"
            ],
            "next_steps": [
                "Add form validation",
                "Integrate with API"
            ]
        },
        work_in_progress={
            "files_modified": ["src/components/LoginForm.tsx"],
            "branch": "feature/login-form",
            "uncommitted_changes": True
        },
        context_snapshot={
            "last_task": "Implement login form",
            "blocked_on": None
        },
        communication_log=[
            {
                "time": datetime.utcnow().isoformat(),
                "type": "message_sent",
                "to": "backend-001",
                "message": "Need API endpoint for login"
            }
        ]
    )

    # Save checkpoint
    checkpoint_file = manager.save_checkpoint("frontend-001", checkpoint)
    print(f"✓ Saved checkpoint: {checkpoint_file}")

    # List checkpoints
    checkpoints = manager.list_checkpoints("frontend-001")
    print(f"✓ Found {len(checkpoints)} checkpoint(s)")

    # Load latest checkpoint
    loaded = manager.load_latest_checkpoint("frontend-001")
    if loaded:
        print(f"✓ Loaded checkpoint for {loaded.agent_id}")
        print(f"  - Role: {loaded.role}")
        print(f"  - Task: {loaded.task_id}")
        print(f"  - Step: {loaded.state.get('current_step', 0)}/{loaded.state.get('total_steps', 0)}")

    print("\n✓ Checkpoint system working correctly!")
