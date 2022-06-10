import os
import setuptools

HERE = os.path.abspath(os.path.dirname(__file__))
def _read(name):
    with open(os.path.join(HERE, name), 'r', encoding='utf-8') as f:
        return f.read()

setuptools.setup(
    name="sapcli",
    version="1.0.0",
    author="Jakub Filak",
    description="Command line interface to SAP products",
    long_description=_read("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=("test")),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 6 - Mature",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "pyodata",
        "PyYAML",
    ],
    test_requires=[
        "codecov",
        "flake8",
        "pylint",
        "pytest>=2.7.0",
        "pytest-cov",
    ]
)
