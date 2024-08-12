from setuptools import setup, find_packages

setup(
    name='obsidian_printify',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'markdown',
    ],
    entry_points={
        'console_scripts': [
            'obsprint=obsidian_printify.cli:convert',
        ],
    },
)

