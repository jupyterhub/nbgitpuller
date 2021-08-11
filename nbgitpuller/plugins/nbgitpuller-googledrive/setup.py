from setuptools import setup

setup(
    name="nbgitpuller-googledrive",
    entry_points={
        "nbgitpuller": ["googledrive=googledrive_puller"]
    },
    py_modules=["googledrive_puller"]
)
