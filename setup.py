import pathlib

from setuptools import setup, find_packages

# Name of the module
MODULE_NAME = 'generic_parser'


# The directory containing this file
TOPLEVEL_DIR = pathlib.Path(__file__).parent.absolute()
ABOUT_FILE = TOPLEVEL_DIR / MODULE_NAME / "__init__.py"
README = TOPLEVEL_DIR / "README.md"


def about_package(init_posixpath: pathlib.Path) -> dict:
    """
    Return package information defined with dunders in __init__.py as a dictionary, when
    provided with a PosixPath to the __init__.py file.
    """
    about_text: str = init_posixpath.read_text()
    return {
        entry.split(" = ")[0]: entry.split(" = ")[1].strip('"').strip("'")
        for entry in about_text.strip().split("\n")
        if entry.startswith("__")
    }


ABOUT_GENERIC_PARSER = about_package(ABOUT_FILE)

# Dependencies for the module itself
DEPENDENCIES = []

# Extra dependencies for tools
EXTRA_DEPENDENCIES = {
                      'test': ['pytest>=5.2',
                               'pytest-cov>=2.6',
                               'hypothesis>=4.36.2',
                               'attrs>=19.2.0'],
                      'doc': ['sphinx',
                              'travis-sphinx',
                              'sphinx_rtd_theme']
                      }

# The text of the README file
with README.open("r") as docs:
    long_description = docs.read()

# This call to setup() does all the work
setup(
    name=ABOUT_GENERIC_PARSER['__title__'],
    version=ABOUT_GENERIC_PARSER['__version__'],
    description=ABOUT_GENERIC_PARSER['__description__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=ABOUT_GENERIC_PARSER['__url__'],
    author=ABOUT_GENERIC_PARSER['__author__'],
    author_email=ABOUT_GENERIC_PARSER['__author_email__'],
    license=ABOUT_GENERIC_PARSER['__license__'],
    python_requires=">=3.6",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(include=('generic_parser',)),
    install_requires=DEPENDENCIES,
    tests_require=EXTRA_DEPENDENCIES['test'],
    extras_require=EXTRA_DEPENDENCIES
)
