from traitlets import Bool
from traitlets.config import Configurable


class NbGitPullerFeatures(Configurable):
    """
    Traitlet used to configure enabling / disabling various nbgitpuller features
    """
    enable_targetpath = Bool(
        False,
        config=True,
        help="""
        Allow setting `targetPath` in the url to specify where the repo should be cloned.

        Set to False to disable, for higher security
        """
    )

