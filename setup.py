from setuptools import find_packages, setup
from distutils.util import convert_path

# Imports __version__, reference: https://stackoverflow.com/a/24517154/2220152
ns = {}
ver_path = convert_path("nbfetch/version.py")
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)
__version__ = ns["__version__"]

setup(
    name="nbfetch",
    version=__version__,
    url="",
    license="3-clause BSD",
    author="Peter Veerman, YuviPanda",
    author_email="peterkangveerman@gmail.com",
    description="Notebook Extension to do one-way synchronization of git repositories",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["notebook>=5.5.0", "tornado", "hs_restclient"],
    data_files=[
        ("etc/jupyter/jupyter_notebook_config.d", ["nbfetch/etc/nbfetch.json"])
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "nbfetch = nbfetch.pull:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
