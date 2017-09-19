from setuptools import find_packages, setup

setup(
    name='nbgitpuller',
    version='0.2',
    url='https://github.com/data-8/nbgitpuller',
    license='BSD',
    author='Peter Veerman',
    author_email='peterkangveerman@gmail.com',
    description='Notebook Extension to do one-way synchronization of git repositories',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['notebook'],
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
