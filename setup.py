from setuptools import find_packages, setup
from distutils.util import convert_path
import subprocess

# Imports __version__, reference: https://stackoverflow.com/a/24517154/2220152
ns = {}
ver_path = convert_path('nbgitpuller/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)
__version__ = ns['__version__']

subprocess.check_call(['npm', 'install'])
subprocess.check_call(['npm', 'run', 'webpack'])

setup(
    name='nbgitpuller',
    version=__version__,
    url='https://github.com/jupyterhub/nbgitpuller',
    license='3-clause BSD',
    author='Peter Veerman, YuviPanda',
    author_email='peterkangveerman@gmail.com',
    description='Notebook Extension to do one-way synchronization of git repositories',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['notebook>=5.5.0', 'tornado'],
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
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
