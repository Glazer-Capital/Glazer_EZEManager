from setuptools import setup, find_packages

setup(
    name='GLAZER_EZE_REST',
    version='0.1.0',
    packages=['GLAZER_EZE_REST']
)

setup(
    name='GLAZER_EZE_REST',  # Replace with your package name
    version='0.1',  # the version of your package
    description='A REST API client for Glazer Eze services',  # Short description
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        'requests',
        'pandas',
        'datetime',
        'os'
    ],
    python_requires='>=3.6',  # Minimum version requirement of Python
)