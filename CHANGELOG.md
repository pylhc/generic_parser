# Generic-Parser Changelog

## Version 1.1.1
 * add a dictionary to the eval in DictFromString to allow reading in *.ini with nans
 

## Version 1.0.8
 * revamp of the documentation
 * fixed a format string error when a choice is not correct for a list argument
 * fixed a setenv issue for Github actions

## Version 1.0.7
 * fixed crash before proper error message for invalid choice of non-string
 objects. 
 * fixed: Paths can be handled by `save_options_to_config` (converted to strings)
 * fixed: Quotes around Paths are stripped from config files on reading
 * fixes: Strings with linebreaks are now written properly with `save_options_to_config`
 * fixed `None` write and read in config files.
 * added tests for list-lengths of default parameters.
 * improved `create_parameter_help` function.
 * some documentation fixed/additions.
 * switched to github actions for CI.
 

## Version 1.0.6
 * Fix KeyError for unknown flags

## Version 1.0.5
 * Re-release of 1.0.4 on pypi due to release errors

## Version 1.0.4
 * remove .idea files

## Version 1.0.3
 - Fixed:
   * pep8 errors and warnings
   * typo in logging
 * Enhancement:
   * Flags default to name if not set 

## Version 1.0.2
 - Fixed:
   - Imports everywhere

## Version 1.0.1
 - Fixed:
   - Imports in \_\_init\_\_

## Version 1.0.0
 - Initial Release
