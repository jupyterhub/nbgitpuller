"""
Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.
"""
from setuptools import find_packages, setup

dependencies = []

setup(
    name='gitautosync',
    version='0.0.1',
    url='https://github.com/data-8/gitautosync',
    license='BSD',
    author='Peter Veerman',
    author_email='peterkangveerman@gmail.com',
    description='Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'gitautosync = gitautosync:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
