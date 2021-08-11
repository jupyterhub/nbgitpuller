from setuptools import setup

setup(
    name="nbgitpuller-dropbox",
    entry_points={
        "nbgitpuller": ["dropbox=dropbox_puller"]
    },
    py_modules=["dropbox_puller"]
)
