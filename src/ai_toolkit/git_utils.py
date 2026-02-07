import warnings
# Suppress the specific ResourceWarning for subprocess on Windows
warnings.filterwarnings("ignore", category=ResourceWarning, module="subprocess")

from typing import Optional, Literal
from git import Repo, GitCommandError


DiffMode = Literal["staged", "uncommitted"]


class GitHelper:
    """Utility wrapper around GitPython for common git operations.

    Methods here raise GitPython exceptions (e.g., GitCommandError) to allow
    callers to decide how to handle errors and display messages.
    """

    @staticmethod
    def get_repo() -> Repo:
        repo = Repo(search_parent_directories=True)
        return repo

    @staticmethod
    def get_diff(mode: DiffMode = "staged") -> Optional[str]:
        """Return the git diff based on the specified mode.

        Args:
            mode: Either "staged" for staged changes or "uncommitted" for unstaged changes.

        Returns:
            The diff output as a string, or None if there are no changes.

        Raises:
            GitCommandError: If git command fails.
        """
        if mode == "staged":
            return GitHelper._staged_diff()
        elif mode == "uncommitted":
            return GitHelper._uncommitted_diff()
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'staged' or 'uncommitted'.")

    @staticmethod
    def _staged_diff() -> Optional[str]:
        """Return the staged diff (equivalent to `git diff --staged`).

        Returns None when there are no staged changes.
        """
        repo = GitHelper.get_repo()
        try:
            diff_output = repo.git.diff("--staged")
            return diff_output if diff_output else None
        except GitCommandError as e:
            # Optionally log or handle the error here
            raise
        finally:
            repo.close()

    @staticmethod
    def _uncommitted_diff() -> Optional[str]:
        """Return the uncommitted diff (equivalent to `git diff`).

        Returns None when there are no uncommitted changes.
        Includes untracked files in the diff output.
        """
        repo = GitHelper.get_repo()
        try:
            # Get diff of tracked files
            diff_output = repo.git.diff()
            
            # Get untracked files
            untracked_files = repo.untracked_files
            
            # If there are untracked files, append their content to diff
            if untracked_files:
                untracked_diff = "\n\n# Untracked files:\n"
                for file_path in untracked_files:
                    untracked_diff += f"\n+++ b/{file_path}\n"
                    try:
                        with open(repo.working_dir + "/" + file_path, 'r', encoding='utf-8', errors='ignore') as f: # type: ignore
                            content = f.read()
                            for line in content.splitlines():
                                untracked_diff += f"+{line}\n"
                    except Exception:
                        untracked_diff += f"(binary or unreadable file)\n"
                
                diff_output = (diff_output + untracked_diff) if diff_output else untracked_diff
            
            return diff_output if diff_output else None
        except GitCommandError as e:
            # Optionally log or handle the error here
            raise
        finally:
            repo.close()

    @staticmethod
    def commit(message: str) -> None:
        """Create a commit with the provided message using the repo index."""
        repo = GitHelper.get_repo()
        try:
            repo.index.commit(message)
        except GitCommandError as e:
            # Optionally log or handle the error here
            raise
        finally:
            repo.close()
