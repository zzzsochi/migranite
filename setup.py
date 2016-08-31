from setuptools import setup, find_packages

setup(
    name='migranite',
    description='Migranite -- manage migtations tool',
    version='0.4.0',
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development",
    ],
    url='https://github.com/zzzsochi/migranite',
    keywords=['migrations', 'development'],
    packages=find_packages(),
    install_requires=['zini', 'python-dateutil', 'colorama'],
    extras_require={'mongo': ['pymongo']},
    entry_points={
        'console_scripts': [
            'migranite = migranite.__main__:main',
        ],
    },
)
