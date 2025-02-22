from jupyter_packaging import wrap_installers, npm_builder
from setuptools import find_packages, setup
import os.path

HERE = os.path.abspath(os.path.dirname(__file__))

# Representative files that should exist after a successful build
jstargets = [
    os.path.join(HERE, "nbgitpuller", "static", "dist", "bundle.js"),
]

# https://github.com/jupyter/jupyter-packaging/blob/0.10.4/README.md#as-a-build-requirement
# https://github.com/jupyter/jupyter-packaging/blob/0.10.4/jupyter_packaging/setupbase.py#L160-L164
jsdeps = npm_builder(build_cmd="webpack", build_dir="nbgitpuller/static/dist", source_dir="nbgitpuller/static/js")
cmdclass = wrap_installers(
    pre_develop=jsdeps, pre_dist=jsdeps,
    ensured_targets=jstargets)

setup(
    name='nbgitpuller',
    version="1.2.3.dev",
    url='https://github.com/jupyterhub/nbgitpuller',
    license='3-clause BSD',
    author='Peter Veerman, YuviPanda',
    author_email='peterkangveerman@gmail.com',
    cmdclass=cmdclass,
    description='Jupyter Extension to do one-way synchronization of git repositories',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['jupyter_server>=1.10.1', 'tornado'],
    data_files=[
        ('etc/jupyter/jupyter_server_config.d', ['nbgitpuller/etc/jupyter_server_config.d/nbgitpuller.json']),
        ('etc/jupyter/jupyter_notebook_config.d', ['nbgitpuller/etc/jupyter_notebook_config.d/nbgitpuller.json'])
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'gitpuller = nbgitpuller.pull:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
