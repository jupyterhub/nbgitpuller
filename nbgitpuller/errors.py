import subprocess
import traceback


class GitPullerError(Exception):
    """
    Structured error class used to branch frontend UI content based on its attributes.

    Attributes:
        code (str): Stable internal error code identifying the failure
            type (e.g. ``"merge"``, ``"clone"``). This value is used by the
            frontend to branch context specific UI behaviour.
        message (str): External error message. This value is
            safe to display in the frontend.
        traceback (Optional[str]): Formatted traceback information captured from
            the original exception for logging.    
    """
    def __init__(self, code: str = "unknown", message: str = "Unexpected error occurred", traceback_message=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.traceback = traceback_message


    def __str__(self):
        return self.message


    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "traceback": self.traceback
        }

    @staticmethod
    def format_traceback(exc):
        tb = getattr(exc, "__traceback__", None)
        traceback_message = ''.join(traceback.format_exception(type(exc), exc, tb)) if tb else None
        return traceback_message


    @classmethod
    def from_exception(cls, exc: Exception) -> "GitPullerError":
        """
        Convert exceptions into a structured GitPullerError class.
        """
        if isinstance(exc, GitPullerError):
            return exc
        traceback_message = cls.format_traceback(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            # Categorise errors based on specific git commands
            if exc.cmd[1] == "clone":
                return CloneError(traceback_message)
            elif len(exc.cmd) >5 and exc.cmd[5] == "merge":
                return MergeError(traceback_message)
            elif exc.cmd[1] == "ls-remote":
                return RemoteError(traceback_message)                
        return cls(code="unknown", message=str(exc), traceback_message=traceback_message)



class CloneError(GitPullerError):
    code="clone"
    message="Clone error detected"

    def __init__(self, traceback_message=None):
        super().__init__(
            code = self.code,
            message= self.message,
            traceback_message=traceback_message
        )


class MergeError(GitPullerError):
    code="merge"
    message="Merge error detected"

    def __init__(self, traceback_message=None):
        super().__init__(
            code = self.code,
            message= self.message,
            traceback_message=traceback_message
        )

class BranchExistError(GitPullerError):
    code="branch_exist"
    message="Branch does not exist"

    def __init__(self, traceback_message=None):
        super().__init__(
            code = self.code,
            message= self.message,
            traceback_message=traceback_message
        )

class BranchResolveError(GitPullerError):
    code="branch_resolve"
    message="Branch name unresolved"

    def __init__(self, traceback_message=None):
        super().__init__(
            code = self.code,
            message= self.message,
            traceback_message=traceback_message
        )

class RemoteError(GitPullerError):
    code="ls_remote"
    message="Remote content unavailable"

    def __init__(self, traceback_message=None):
        super().__init__(
            code = self.code,
            message= self.message,
            traceback_message=traceback_message
        )
