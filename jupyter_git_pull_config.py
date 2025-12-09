# May be set to a list of URLs described as Python regular expressions (using re.fullmatch())
# where it is permitted to autorun scripts from the pulled project as a pre-initialisation
# step.
#
# WARNING: Enable this only if you understand and accept the risks of AUTORUN.INF.
# ----
# c.NbGitPuller.autorun_allow = [
#   r'https://github\.com/org/name\.git',
#   r'https://github\.com/org-two/name-two\.git'
# ]
# ----
#
# To allow all sources (*not* recommended) use:
# ----
# c.NbGitPuller.autorun_allow = True
# ----
#
# The default is 'False' which means the autorun functionality is completely disabled
#c.NbGitPuller.autorun_allow = False

# List of scripts to search for when attempting to autorun. The first match will
# be run with a single argument of 'init' or 'update' depending on what nbgitpuller
# is doing.
# ----
# c.NbGitPuller.autorun_script = [
#   '.nbgitpuller.script',
#   '.different.script'
# ]
# ----
#
# The 'script' must be executable and when checked out on a 'exec' (ie. not a 'noexec') mountpoint
#
# The default is the empty list.
#c.NbGitPuller.autorun_script = []
