from setuptools import setup, find_packages

setup(
    name="rlwe_xmkckks",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy==1.24.2',
    ],
)