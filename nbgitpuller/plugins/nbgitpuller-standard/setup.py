from setuptools import setup

setup(
    name="nbgitpuller-standard",
    entry_points={
        "nbgitpuller": ["standard=standardweb_puller"]
    },
    py_modules=["standardweb_puller"]
)
