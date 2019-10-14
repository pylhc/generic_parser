import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="generic-parser",
    version="1.0.5",
    description="A parser for arguments and config-files that also allows direct python input.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pylhc/generic_parser",
    author="pyLHC",
    author_email="pylhc@github.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["generic_parser"],
    install_requires=[],
)
