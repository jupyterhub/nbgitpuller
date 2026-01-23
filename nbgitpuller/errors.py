import subprocess
import traceback


class GitPullerError(Exception):
    code="unknown"
    helper_message="An unexpected error occurred during synchronization."

    def __init__(self, traceback_message=None):
        self.traceback = traceback_message


    def to_dict(self):
        return {
            "code": self.code,
            "message": self.helper_message,
            "traceback": self.traceback
        }

    @classmethod
    def from_exception(cls, exc: Exception):
        """
        Convert exceptions into a structured GitPullerError class.
        """
        tb = getattr(exc, "__traceback__", None)
        traceback_message = ''.join(traceback.format_exception(type(exc), exc, tb)) if tb else None
        if isinstance(exc, subprocess.CalledProcessError):
            if "merge" in exc.cmd:
                return MergeConflictError(traceback_message)
        return cls(traceback_message)


class MergeConflictError(GitPullerError):
    code="merge_conflict"
    helper_message="Unresolvable conflicts detected while syncing."

    def __init__(self, traceback_message=None):
        super().__init__(traceback_message)