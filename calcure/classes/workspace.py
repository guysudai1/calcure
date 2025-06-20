from pathlib import Path


class Workspace:
    def __init__(self, workspace_path: Path | str) -> None:
        self.workspace_path = workspace_path

        # Note: this could be a property but it's nice if we ever want to change it ad-hoc
        self.workspace_lock = f"{self.workspace_path}.lock" 

    def __eq__(self, other):
        if isinstance(other, Workspace):
            return self.workspace_path == other.workspace_path and self.workspace_lock == other.workspace_lock

        raise NotImplementedError()