"""
Progress tracking module for autonomous task agent.

Implements file-based state management using:
- progress.txt: Human-readable log of work completed
- feature_list.json: Structured task tracking
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class FeatureStatus(str, Enum):
    """Status of a feature in the task list."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"


@dataclass
class Feature:
    """A feature/task to be implemented."""
    id: str
    name: str
    description: str
    status: FeatureStatus = FeatureStatus.PENDING
    files: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "files": self.files,
            "blockers": self.blockers,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Feature":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            status=FeatureStatus(data.get("status", "pending")),
            files=data.get("files", []),
            blockers=data.get("blockers", []),
            completed_at=data.get("completed_at"),
        )


@dataclass
class FeatureList:
    """Collection of features for a task."""
    task_description: str
    features: list[Feature] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "task_description": self.task_description,
            "features": [f.to_dict() for f in self.features],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FeatureList":
        """Create from dictionary."""
        return cls(
            task_description=data["task_description"],
            features=[Feature.from_dict(f) for f in data.get("features", [])],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
        )

    def get_next_pending(self) -> Optional[Feature]:
        """Get the next pending feature."""
        for feature in self.features:
            if feature.status == FeatureStatus.PENDING:
                return feature
        return None

    def get_in_progress(self) -> list[Feature]:
        """Get all in-progress features."""
        return [f for f in self.features if f.status == FeatureStatus.IN_PROGRESS]

    def get_completed(self) -> list[Feature]:
        """Get all completed features."""
        return [f for f in self.features if f.status == FeatureStatus.COMPLETE]

    def is_complete(self) -> bool:
        """Check if all features are complete."""
        return all(f.status == FeatureStatus.COMPLETE for f in self.features)

    def completion_percentage(self) -> float:
        """Get completion percentage."""
        if not self.features:
            return 0.0
        completed = len(self.get_completed())
        return (completed / len(self.features)) * 100


class ProgressTracker:
    """Manages progress tracking for the autonomous agent."""

    def __init__(
        self,
        progress_file: str = "progress.txt",
        feature_file: str = "feature_list.json",
    ):
        self.progress_path = Path(progress_file)
        self.feature_path = Path(feature_file)
        self._feature_list: Optional[FeatureList] = None

    def has_existing_state(self) -> bool:
        """Check if there's existing state to resume from."""
        return self.feature_path.exists()

    def load_feature_list(self) -> Optional[FeatureList]:
        """Load feature list from file."""
        if not self.feature_path.exists():
            return None

        try:
            with open(self.feature_path, "r") as f:
                data = json.load(f)
            self._feature_list = FeatureList.from_dict(data)
            return self._feature_list
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading feature list: {e}")
            return None

    def save_feature_list(self, feature_list: FeatureList) -> None:
        """Save feature list to file."""
        feature_list.updated_at = datetime.utcnow().isoformat()
        self._feature_list = feature_list

        with open(self.feature_path, "w") as f:
            json.dump(feature_list.to_dict(), f, indent=2)

    def log_progress(self, message: str, include_timestamp: bool = True) -> None:
        """Append a progress entry to the log file."""
        timestamp = ""
        if include_timestamp:
            timestamp = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] "

        with open(self.progress_path, "a") as f:
            f.write(f"{timestamp}{message}\n")

    def log_section(self, title: str) -> None:
        """Log a section header."""
        separator = "=" * 50
        self.log_progress(f"\n{separator}", include_timestamp=False)
        self.log_progress(f"## {title}", include_timestamp=False)
        self.log_progress(separator, include_timestamp=False)

    def read_progress(self) -> str:
        """Read the full progress log."""
        if not self.progress_path.exists():
            return ""
        return self.progress_path.read_text()

    def mark_feature_started(self, feature_id: str) -> None:
        """Mark a feature as in progress."""
        if not self._feature_list:
            self.load_feature_list()

        if not self._feature_list:
            return

        for feature in self._feature_list.features:
            if feature.id == feature_id:
                feature.status = FeatureStatus.IN_PROGRESS
                self.save_feature_list(self._feature_list)
                self.log_progress(f"Started: {feature.name}")
                break

    def mark_feature_complete(
        self,
        feature_id: str,
        files_modified: Optional[list[str]] = None
    ) -> None:
        """Mark a feature as complete."""
        if not self._feature_list:
            self.load_feature_list()

        if not self._feature_list:
            return

        for feature in self._feature_list.features:
            if feature.id == feature_id:
                feature.status = FeatureStatus.COMPLETE
                feature.completed_at = datetime.utcnow().isoformat()
                if files_modified:
                    feature.files.extend(files_modified)
                self.save_feature_list(self._feature_list)
                self.log_progress(f"Completed: {feature.name}")
                break

    def mark_feature_blocked(
        self,
        feature_id: str,
        blockers: list[str]
    ) -> None:
        """Mark a feature as blocked."""
        if not self._feature_list:
            self.load_feature_list()

        if not self._feature_list:
            return

        for feature in self._feature_list.features:
            if feature.id == feature_id:
                feature.status = FeatureStatus.BLOCKED
                feature.blockers = blockers
                self.save_feature_list(self._feature_list)
                self.log_progress(f"Blocked: {feature.name} - {', '.join(blockers)}")
                break

    def get_summary(self) -> str:
        """Get a summary of current progress."""
        if not self._feature_list:
            self.load_feature_list()

        if not self._feature_list:
            return "No task initialized"

        total = len(self._feature_list.features)
        completed = len(self._feature_list.get_completed())
        in_progress = len(self._feature_list.get_in_progress())
        blocked = len([f for f in self._feature_list.features if f.status == FeatureStatus.BLOCKED])
        pending = total - completed - in_progress - blocked

        return f"""Progress Summary
================
Task: {self._feature_list.task_description}

Status:
  Completed:   {completed}/{total} ({self._feature_list.completion_percentage():.1f}%)
  In Progress: {in_progress}
  Blocked:     {blocked}
  Pending:     {pending}
"""


def create_initial_feature_list(
    task_description: str,
    features: list[dict]
) -> FeatureList:
    """Helper to create a feature list from a task description."""
    feature_objects = []
    for i, f in enumerate(features):
        feature_objects.append(Feature(
            id=f.get("id", f"feature-{i+1}"),
            name=f["name"],
            description=f.get("description", f["name"]),
        ))

    return FeatureList(
        task_description=task_description,
        features=feature_objects,
    )


if __name__ == "__main__":
    # Demo usage
    tracker = ProgressTracker()

    # Create initial state
    features = [
        {"name": "User authentication", "description": "JWT-based auth"},
        {"name": "User CRUD endpoints", "description": "Create, read, update, delete"},
        {"name": "Input validation", "description": "Validate all inputs"},
    ]

    feature_list = create_initial_feature_list(
        "Build a REST API for user management",
        features
    )

    tracker.save_feature_list(feature_list)
    tracker.log_section("Task Initialized")
    tracker.log_progress("Created feature list with 3 features")

    print(tracker.get_summary())
