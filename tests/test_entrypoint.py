import logging
import sys

import pytest
from tests.conftest import cli_args

from generic_parser.dict_parser import ParameterError, ArgumentError
from generic_parser.entry_datatypes import get_multi_class, DictAsString, BoolOrString, BoolOrList
from generic_parser.entrypoint_parser import (EntryPointParameters,
                                              entrypoint, EntryPoint,
                                              OptionsError, split_arguments,
                                              create_parameter_help, save_options_to_config
                                              )
from generic_parser.tools import silence, print_dict_tree, TempStringLogger


LOG = logging.getLogger(__name__)
DEBUG = False


# Tests ########################################################################


# Options Tests


def test_strict_wrapper_fail():
    with pytest.raises(OptionsError):
        @entrypoint(get_simple_params(), strict=True)
        def strict(opt, unknown):  # too many option-structures
            pass


def test_class_wrapper_fail():
    with pytest.raises(OptionsError):
        class MyClass(object):
            @entrypoint(get_simple_params())
            def fun(self, opt):  # too few option-structures
                pass


def test_normal_wrapper_fail():
    with pytest.raises(OptionsError):
        @entrypoint(get_simple_params())
        def fun(opt, unknown, more):  # too many option-structures
            pass


def test_class_functions():
    class MyClass(object):
        @classmethod
        @entrypoint(get_simple_params())
        def fun(cls, opt, unknown):
            pass


def test_instance_functions():
    class MyClass(object):
        @entrypoint(get_simple_params())
        def fun(self, opt, unknown):
            pass


# Parameter Tests


def test_wrong_param_creation_name():
    with pytest.raises(ParameterError):
        EntryPoint([{"flags": "--flag"}])


def test_wrong_param_creation_other():
    with pytest.raises(TypeError):
        EntryPoint([{"name": "test", "flags": "--flag", "other": "unknown"}])


def test_choices_not_iterable():
    with pytest.raises((ParameterError, ValueError)):
        # Value error comes from argparse (would be caught in dict_parser as well)
        EntryPoint([{"name": "test", "flags": "--flag",
                     "choices": 3,
                     }])


def test_empty_list_default_for_nargs_plus():
    with pytest.raises(ParameterError):
        EntryPoint([{"name": "test", "nargs": "+", "default": []}])


def test_wrong_length_default_for_nargs():
    with pytest.raises(ParameterError):
        EntryPoint([{"name": "test", "nargs": 2, "default": [1, 2, 3]}])


def test_missing_flag_replaced_by_name():
    ep = EntryPoint([{"name": "test"}])

    assert len(ep.parameter[0]) == 2
    assert ep.parameter[0]['flags'] == ['--test']
    assert ep.parameter[0]['name'] == 'test'


def test_missing_flag_replaced_by_name_in_multiple_lists():
    ep = EntryPoint([{"name": "test"},
                     {"name": "thermos_coffee"},
                     {"name": "tee_kessel", "flags": ['--tee_kessel']}])

    assert len(ep.parameter[0]) == 2
    assert ep.parameter[0]['flags'] == ['--test']
    assert ep.parameter[0]['name'] == 'test'

    assert len(ep.parameter[1]) == 2
    assert ep.parameter[1]['flags'] == ['--thermos_coffee']
    assert ep.parameter[1]['name'] == 'thermos_coffee'

    assert len(ep.parameter[2]) == 2
    assert ep.parameter[2]['flags'] == ['--tee_kessel']
    assert ep.parameter[2]['name'] == 'tee_kessel'


# Argument Tests


def test_strict_pass():
    strict_function(accel="LHCB1", anint=3)


def test_strict_fail():
    with pytest.raises(ArgumentError):
        strict_function(accel="LHCB1", anint=3, unkown="not_found")


def test_as_kwargs():
    opt, unknown = paramtest_function(
        name="myname",
        int=3,
        list=[4, 5, 6],
        unknown="myfinalargument"
    )
    assert opt.name == "myname"
    assert opt.int == 3
    assert len(opt.list) == 3
    assert opt.list[1] == 5
    assert len(unknown) > 0


def test_as_string():
    opt, unknown = paramtest_function(
        ["--name", "myname",
         "--int", "3",
         "--list", "4", "5", "6",
         "--other"]
    )
    assert opt.name == "myname"
    assert opt.int == 3
    assert len(opt.list) == 3
    assert opt.list[1] == 5
    assert len(unknown) > 0


def test_as_argv():  # almost identical to above
    with cli_args("--name", "myname", "--int", "3", "--list", "4", "5", "6",
                  "--other"):
        opt, unknown = paramtest_function()
        assert opt.name == "myname"
        assert opt.int == 3
        assert len(opt.list) == 3
        assert opt.list[1] == 5
        assert len(unknown) > 0


def test_as_config(tmp_output_dir):
    cfg_file = tmp_output_dir / "config.ini"
    with open(cfg_file, "w") as f:
        f.write("\n".join([
            "[Section]",
            "name = 'myname'",
            "int = 3",
            "list = [4, 5, 6]",
            "unknown = 'other'",
        ]))

    # test config as kwarg
    opt1, unknown1 = paramtest_function(
        entry_cfg=cfg_file, section="Section"
    )

    # test config as commandline args
    opt2, unknown2 = paramtest_function(
        ["--entry_cfg", str(cfg_file), "--section", "Section"]
    )

    assert opt1.name == "myname"
    assert opt1.int == 3
    assert len(opt1.list) == 3
    assert opt1.list[1] == 5
    assert len(unknown1) > 0

    assert opt2.name == "myname"
    assert opt2.int == 3
    assert len(opt2.list) == 3
    assert opt2.list[1] == 5
    assert len(unknown2) > 0


def test_all_missing():
    with pytest.raises(SystemExit):
        with silence():
            some_function()


def test_required_missing():
    with pytest.raises(ArgumentError):
        some_function(accel="LHCB1")


def test_wrong_choice():
    with pytest.raises(ArgumentError):
        some_function(accel="accel", anint=3)


def test_wrong_type():
    with pytest.raises(ArgumentError):
        some_function(accel="LHCB1", anint=3.)


def test_wrong_type_in_list():
    with pytest.raises(ArgumentError):
        some_function(accel="LHCB1", anint=3, alist=["a", "b"])


def test_not_enough_length():
    with pytest.raises(ArgumentError):
        some_function(accel="LHCB1", anint=3, alist=[])


def test_optional_parameter_no_default_accepts_none():
    @entrypoint(dict(foo=dict(required=False)), strict=True)
    def fun(opt):
        return opt

    opt = fun(foo=None)
    assert opt.foo == None


def test_optional_list_parameter_no_default_accepts_none():
    @entrypoint(dict(foo=dict(required=False, nargs=3)), strict=True)
    def fun(opt):
        return opt

    opt = fun(foo=None)
    assert opt.foo == None


def test_optional_parameter_default_accepts_none():
    @entrypoint(dict(foo=dict(required=False, default='test')), strict=True)
    def fun(opt):
        return opt

    opt = fun({})
    assert opt.foo == 'test'

    opt = fun(foo=None)
    assert opt.foo == None


def test_required_parameter_does_not_accept_none():
    @entrypoint(dict(foo=dict(required=True)), strict=True)
    def fun(opt):
        return opt

    with pytest.raises(ArgumentError):
        fun(foo=None)


# Config Saver Test

def test_save_options(tmp_output_dir):
    opt, unknown = paramtest_function(
        name="myname",
        int=3,
        list=[4, 5, 6],
        unknown="myfinalargument",
        unknoown=10,
    )
    cfg_file = tmp_output_dir / "config.ini"
    save_options_to_config(cfg_file, opt, unknown)
    opt_load, unknown_load = paramtest_function(entry_cfg=cfg_file)

    _assert_dicts_equal(opt, opt_load)
    _assert_dicts_equal(unknown, unknown_load)


def test_save_cli_options(tmp_output_dir):
    opt, unknown = paramtest_function(
        ["--name", "myname",
         "--int", "3",
         "--list", "4", "5", "6",
         "--other"]
    )
    cfg_file = tmp_output_dir / "config.ini"
    save_options_to_config(cfg_file, opt, unknown)
    opt_load, unknown_load = paramtest_function(entry_cfg=cfg_file)

    _assert_dicts_equal(opt, opt_load)
    assert len(unknown_load) == 0


def test_save_and_load_with_none(tmp_output_dir):
    # use cli_args in case we run in test-wrapper (e.g. pycharm)
    with cli_args():  # name, int, list = None
        opt, unknown = paramtest_function()

    cfg_file = tmp_output_dir / "config.ini"
    save_options_to_config(cfg_file, opt, unknown)
    opt_load, unknown_load = paramtest_function(entry_cfg=cfg_file)

    _assert_dicts_equal(opt, opt_load)
    assert len(unknown) == 0
    assert len(unknown_load) == 0
    assert all([val is None for val in opt.values()])


def test_save_and_load_with_none_explicit(tmp_output_dir):
    opt, unknown = paramtest_function(name=None, int=None, list=None)

    cfg_file = tmp_output_dir / "config.ini"
    save_options_to_config(cfg_file, opt, unknown)
    opt_load, unknown_load = paramtest_function(entry_cfg=cfg_file)

    _assert_dicts_equal(opt, opt_load)
    assert len(unknown) == 0
    assert len(unknown_load) == 0
    assert all([val is None for val in opt.values()])


def _assert_dicts_equal(d1, d2):
    for key in d1:
        assert d1[key] == d2[key]
    assert len(d2) == len(d1)


# Test Special Datatypes


def test_multiclass_class():
    float_str = get_multi_class(float, str)
    assert isinstance(1., float_str)
    assert isinstance("", float_str)
    assert isinstance(float_str(1.), float)
    assert isinstance(float_str(1), float)
    assert not isinstance(float_str(1), int)
    assert float_str("myString") == "myString"
    assert issubclass(str, float_str)
    assert issubclass(float, float_str)


def test_dict_as_string_class():
    assert isinstance({}, DictAsString)
    assert isinstance("", DictAsString)
    assert isinstance(DictAsString("{}"), dict)
    assert issubclass(dict, DictAsString)
    assert issubclass(str, DictAsString)

    with pytest.raises(ValueError):
        DictAsString("1")


def test_bool_or_str_class():
    assert isinstance(True, BoolOrString)
    assert isinstance("myString", BoolOrString)
    assert BoolOrString("True") is True
    assert BoolOrString("1") is True
    assert BoolOrString(True) is True
    assert BoolOrString(1) is True
    assert BoolOrString("myString") == "myString"
    assert issubclass(bool, BoolOrString)
    assert issubclass(str, BoolOrString)
    assert not issubclass(list, BoolOrString)


def test_bool_or_list_class():
    assert isinstance(True, BoolOrList)
    assert isinstance([], BoolOrList)
    assert BoolOrList("False") is False
    assert BoolOrList("0") is False
    assert BoolOrList(False) is False
    assert BoolOrList(0) is False
    assert BoolOrList("[1, 2]") == [1, 2]
    assert issubclass(bool, BoolOrList)
    assert issubclass(list, BoolOrList)
    assert not issubclass(str, BoolOrList)


def test_multiclass():
    IntOrStr = get_multi_class(int, str)

    @entrypoint([dict(flags="--ios", name="ios", type=IntOrStr)], strict=True)
    def fun(opt):
        return opt

    opt = fun(ios=3)
    assert opt.ios == 3

    opt = fun(ios='3')
    assert opt.ios == '3'

    opt = fun(["--ios", "3"])
    assert opt.ios == 3

    opt = fun(["--ios", "'3'"])
    assert opt.ios == "'3'"


def test_dict_as_string():
    @entrypoint([dict(flags="--dict", name="dict", type=DictAsString)], strict=True)
    def fun(opt):
        return opt

    opt = fun(dict={'int': 5, 'str': 'hello'})
    assert opt.dict['int'] == 5
    assert opt.dict['str'] == 'hello'

    opt = fun(["--dict", "{'int': 5, 'str': 'hello'}"])
    assert opt.dict['int'] == 5
    assert opt.dict['str'] == 'hello'


def test_bool_or_str(tmp_output_dir):
    @entrypoint([dict(flags="--bos", name="bos", type=BoolOrString)], strict=True)
    def fun(opt):
        return opt

    opt = fun(bos=True)
    assert opt.bos is True

    opt = fun(bos='myString')
    assert opt.bos == 'myString'

    opt = fun(["--bos", "False"])
    assert opt.bos is False

    opt = fun(["--bos", "1"])
    assert opt.bos is True

    opt = fun(["--bos", "myString"])
    assert opt.bos == "myString"

    cfg_file = tmp_output_dir / "bos.ini"
    with open(cfg_file, "w") as f:
        f.write("[Section]\nbos = 'myString'")
    opt = fun(entry_cfg=cfg_file)
    assert opt.bos == "myString"


def test_bool_or_str_cfg(tmp_output_dir):
    @entrypoint([dict(flags="--bos1", name="bos1", type=BoolOrString),
                 dict(flags="--bos2", name="bos2", type=BoolOrString)], strict=True)
    def fun(opt):
        return opt

    cfg_file = tmp_output_dir / "bos.ini"
    with open(cfg_file, "w") as f:
        f.write("[Section]\nbos1 = 'myString'\nbos2 = True")
    opt = fun(entry_cfg=cfg_file)
    assert opt.bos1 == 'myString'
    assert opt.bos2 is True


def test_bool_or_list():
    @entrypoint([dict(flags="--bol", name="bol", type=BoolOrList)], strict=True)
    def fun(opt):
        return opt

    opt = fun(bol=True)
    assert opt.bol is True

    opt = fun(bol=[1, 2])
    assert opt.bol == [1, 2]

    opt = fun(["--bol", "[1, 2]"])
    assert opt.bol == [1, 2]

    opt = fun(["--bol", "0"])
    assert opt.bol is False

    opt = fun(["--bol", "True"])
    assert opt.bol is True


def test_bool_or_list_cfg(tmp_output_dir):
    @entrypoint([dict(flags="--bol1", name="bol1", type=BoolOrList),
                 dict(flags="--bol2", name="bol2", type=BoolOrList)], strict=True)
    def fun(opt):
        return opt

    cfg_file = tmp_output_dir / "bol.ini"
    with open(cfg_file, "w") as f:
        f.write("[Section]\nbol1 = 1,2\nbol2 = True")
    opt = fun(entry_cfg=cfg_file)
    assert opt.bol1 == [1, 2]
    assert opt.bol2 is True


# Test the Helpers #################################################################


def test_split_listargs():
    args = ["--a1", "1", "--a2", "2", "--a3", "3"]
    split = split_arguments(args, get_simple_params())
    assert split[0].pop("arg1", None) == "1"
    assert split[0].pop("arg2", None) == "2"
    assert len(split[0]) == 0
    assert split[1] == args[-2:]


def test_split_dictargs():
    args = {"arg1": "1", "arg2": 2, "arg3": 3}
    split = split_arguments(args, get_simple_params())
    assert split[0].pop("arg1", None) == "1"
    assert split[0].pop("arg2", None) == 2
    assert len(split[0]) == 0
    assert split[1].pop("arg3") == 3


def test_create_param_help():
    this_module = sys.modules[__name__]
    entrypoint_module = sys.modules[create_parameter_help.__module__].__name__
    with TempStringLogger(entrypoint_module) as log:
        create_parameter_help(this_module)
    text = log.get_log()
    for name in get_params().keys():
        assert name in text


def test_create_param_help_other():
    this_module = sys.modules[__name__]
    entrypoint_module = sys.modules[create_parameter_help.__module__].__name__
    with TempStringLogger(entrypoint_module) as log:
        create_parameter_help(this_module, "get_other_params")
    text = log.get_log()
    for name in get_other_params().keys():
        assert name in text


# Example Parameter Definitions ################################################


def get_simple_params():
    """ Parameters as a list of dicts, to test this behaviour as well."""
    return [{"name": "arg1", "flags": "--a1", },
            {"name": "arg2", "flags": "--a2", }
            ]


def get_testing_params():
    """ Parameters as a dict of dicts, to test this behaviour as well."""
    return {
        "name": dict(flags="--name", type=str),
        "int": dict(flags="--int", type=int),
        "list": dict(flags="--list", type=int, nargs="+")
    }


def get_params():
    """ Parameters defined with EntryPointArguments (which is a dict *cough*) """
    args = EntryPointParameters()
    args.add_parameter(name="accel",
                       flags=["-a", "--accel"],
                       help="Which accelerator: LHCB1 LHCB2 LHCB4? SPS RHIC TEVATRON",
                       choices=["LHCB1", "LHCB2", "LHCB5"],
                       required=True,
                       )
    args.add_parameter(name="anint",
                       flags=["-i", "--int"],
                       help="Just a number.",
                       type=int,
                       required=True,
                       )
    args.add_parameter(name="alist",
                       flags=["-l", "--lint"],
                       help="Just a number.",
                       type=int,
                       nargs="+",
                       )
    args.add_parameter(name="anotherlist",
                       flags=["-k", "--alint"],
                       help="list.",
                       type=str,
                       nargs=3,
                       default=["a", "c", "f"],
                       choices=["a", "b", "c", "d", "e", "f"],
                       ),
    return args


def get_other_params():
    """ For testing the create_param_help()"""
    args = EntryPointParameters({
        "arg1": dict(flags="--arg1", help="A help.", default=1,),
        "arg2": dict(flags="--arg2", help="More help.", default=2,),
        "arg3": dict(flags="--arg3", help="Even more...", default=3,),
        "arg4": dict(flags="--arg4", help="...heeeeeeeeelp.", default=4,),
    })
    return args


# Example Wrapped Functions ####################################################


@entrypoint(get_params())
def some_function(options, unknown_options):
    LOG.debug("Some Function")
    print_dict_tree(options, print_fun=LOG.debug)
    LOG.debug("Unknown Options: \n {:s}".format(str(unknown_options)))
    LOG.debug("\n")


@entrypoint(get_params(), strict=True)
def strict_function(options):
    LOG.debug("Strict Function")
    print_dict_tree(options, print_fun=LOG.debug)
    LOG.debug("\n")


@entrypoint(get_testing_params())
def paramtest_function(opt, unknown):
    return opt, unknown
