# Generic Parser
[![Cron Testing](https://github.com/pylhc/generic_parser/workflows/Cron%20Testing/badge.svg)](https://github.com/pylhc/generic_parser/actions?query=workflow%3A%22Cron+Testing%22)
[![Code Climate coverage](https://img.shields.io/codeclimate/coverage/pylhc/generic_parser.svg?style=popout)](https://codeclimate.com/github/pylhc/generic_parser)
[![Code Climate maintainability (percentage)](https://img.shields.io/codeclimate/maintainability-percentage/pylhc/generic_parser.svg?style=popout)](https://codeclimate.com/github/pylhc/generic_parser)
<!-- [![GitHub last commit](https://img.shields.io/github/last-commit/pylhc/generic_parser.svg?style=popout)](https://github.com/pylhc/generic_parser/) -->
[![PyPI Version](https://img.shields.io/pypi/v/generic_parser?label=PyPI&logo=pypi)](https://pypi.org/project/generic_parser/)
[![GitHub release](https://img.shields.io/github/v/release/pylhc/generic_parser?logo=github)](https://github.com/pylhc/generic_parser/)
[![Conda-forge Version](https://img.shields.io/conda/vn/conda-forge/generic_parser?color=orange&logo=anaconda)](https://anaconda.org/conda-forge/generic_parser)
[![DOI](https://zenodo.org/badge/201085116.svg)](https://zenodo.org/badge/latestdoi/201085116)

The package provides an all-around parser for arguments and config-files.
The creation of the arguments is similar to the ones from argparse, but the input can then be either from command line, a config file or directly from python.

See the [API documentation](https://pylhc.github.io/generic_parser/) for details.

## Installing

Installation is easily done via `pip`. The package is then used as `generic_parser`.
```bash
python -m pip install generic-parser
```

One can also install in a `conda` environment via the `conda-forge` channel with:
```bash
conda install -c conda-forge generic_parser
```

## Example Usage:

Content of `myscript.py`
```python
from generic_parser import entrypoint, EntryPointParameters


def get_arguments():
    args = EntryPointParameters()
    args.add_parameter(name="first",
                       flags=["-f", "--first"],
                       help="First Parameter, an int",
                       choices=[1, 2, 3],
                       type=int,
                       required=True,
                       )
    args.add_parameter(name="second",
                       flags=["-s", "--second"],
                       help="Second Parameter, a string",
                       type=str,
                       default="default",
                       required=False,
                       )
    return args


@entrypoint(get_arguments())
def main(opt, unknown):
    print(opt.first == 1)
    print(opt.second == "default")


if __name__ == '__main__':
    main()
```

### Commandline

Calling that script with ``python myscript.py -f 1 -s "test"`` will result in:
```
True
False
```

It is assumed, that this is the standard mode of operation for your functions.

#### Config File

Further, one can also use a config file `config.ini` containing:
```
[Section]
first = 2
second = "Hello"
```

and run the script with `python myscript.py --entry_cfg config.ini` leading to
```
False
False
```

Config files are very useful if you want to rerun your code with the same or similar parameters.
Especially the declaration of a `[DEFAULT]` section can be helpful.
For further information about config files, check the python [Config Parser](https://docs.python.org/3/library/configparser.html).

### Python
Or call the function directly from python code:
```python
if __name__ == '__main__':
    main(first=1, second="World")
```

```
True
False
```

This is incredibly helpful if one wants to write python-wrappers around entrypoint-functions,
and does not want to resort to commandline calls from python.

Note that also in this case all variables are validated, courtesy of the `dict_parser`.
`dict_parser` provides even multi-level dictionary checking functionality,
which is not used in the `Entrypoint`, but can be handy in other use-cases.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
