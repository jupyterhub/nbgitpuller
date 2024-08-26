"""Import base Handler classes from Jupyter Server or Notebook

Must be called before importing .handlers to ensure the correct base classes
"""
import warnings

_JupyterHandler = None


def get_base_handler(app=None):
    """Get the base JupyterHandler class to use

    Inferred from app class (either jupyter_server or notebook app)
    """
    global _JupyterHandler
    if _JupyterHandler is not None:
        return _JupyterHandler
    if app is None:
        warnings.warn(
            "Guessing base JupyterHandler class. Specify an app to ensure the right JupyterHandler is used.",
            stacklevel=2,
        )
        from jupyter_server.base.handlers import JupyterHandler
        return JupyterHandler

    top_modules = {cls.__module__.split(".", 1)[0] for cls in app.__class__.mro()}
    if "jupyter_server" in top_modules:
        from jupyter_server.base.handlers import JupyterHandler

        _JupyterHandler = JupyterHandler
        return _JupyterHandler
    if "notebook" in top_modules:
        from notebook.base.handlers import IPythonHandler

        _JupyterHandler = IPythonHandler
        return _JupyterHandler

    warnings.warn(f"Failed to detect base JupyterHandler class for {app}.", stacklevel=2)
    from jupyter_server.base.handlers import JupyterHandler
    return JupyterHandler
