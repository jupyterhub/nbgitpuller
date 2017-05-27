"""
Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.
"""
from setuptools import find_packages, setup

dependencies = ['click', 'git']

setup(
    name='gitautosync',
    version='0.0.1',
    url='https://github.com/SaladRaider/gitautosync',
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
            'gitautosync = gitautosync.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
