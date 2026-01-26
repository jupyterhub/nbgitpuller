import subprocess
import traceback


class GitPullerError(Exception):

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
    def from_exception(cls, exc: Exception):
        """
        Convert exceptions into a structured GitPullerError class.
        """
        traceback_message = cls.format_traceback(exc)
        if isinstance(exc, subprocess.CalledProcessError):
            if "clone" in exc.cmd:
                return CloneError(traceback_message)
            elif "merge" in exc.cmd:
                return MergeError(traceback_message)
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

