from cc_plugin_cmip6_cv.util import accepts
import pytest


# ~~~~~~~~~~~~~~~~~~~~~~ DEFINE TEST DATA ~~~~~~~~~~~~~~~~~~~~~~
# NONE

def test__cv_tools__accepts():
    # see: https://stackoverflow.com/questions/34648337/how-to-test-a-decorator-in-a-python-package/34648674

    # some successful tests
    #   test one type per argument
    @accepts(int, int)
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(1, 2)

    #   test set of types for one argument
    @accepts(int, (int, float))
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(1, 2)

    #   test set of types for one argument; another input
    @accepts(int, (int, float))
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(1, 2.0)

    #   use one argument via keyword
    @accepts(int, float)
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(1, arg2=2.0)

    #   use both arguments via keyword
    @accepts(int, float)
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(arg1=1, arg2=2.0)

    #   use both arguments via keyword, reordered
    @accepts(int, float)
    def dummy_fun(arg1, arg2):
        return arg1+arg2
    assert 3 == dummy_fun(arg2=2.0, arg1=1)

    #   make one argument optional; provide only one arg
    @accepts(int, float)
    def dummy_fun(arg1, arg2=3.0):
        return arg1+arg2
    assert 4 == dummy_fun(1)

    #   make one argument optional; provide only one arg via keyword
    @accepts(int, float)
    def dummy_fun(arg1, arg2=3.0):
        return arg1+arg2
    assert 4 == dummy_fun(arg1=1)

    #   make one argument optional; provide two args (none as kw)
    @accepts(int, float)
    def dummy_fun(arg1, arg2=3.0):
        return arg1+arg2
    assert 3 == dummy_fun(1, 2.0)

    #   make one argument optional; provide two args (both as kw)
    @accepts(int, float)
    def dummy_fun(arg1, arg2=3.0):
        return arg1+arg2
    assert 3 == dummy_fun(arg1=1, arg2=2.0)

    #   make one argument optional; provide two args (both as kw, new order)
    @accepts(int, float)
    def dummy_fun(arg1, arg2=3.0):
        return arg1+arg2
    assert 3 == dummy_fun(arg2=2.0, arg1=1)

    # test with errors
    #   provide less arguments to function than to decorator, RuntimeError
    with pytest.raises(RuntimeError):
        @accepts(int, int)
        def dummy_fun(arg1):
            return arg1
        dummy_fun(1)

    #   provide more arguments to function than to decorator, RuntimeError
    with pytest.raises(RuntimeError):
        @accepts(int, int)
        def dummy_fun(arg1, arg2, arg3):
            return arg1+arg2+arg3
        dummy_fun(1, 2, 3)

    #   provide a wrong type to the function call, TypeError
    with pytest.raises(TypeError):
        @accepts(int, int)
        def dummy_fun(arg1, arg2):
            return arg1+arg2
        dummy_fun(1, 2.0)

    #   provide a wrong type to the function call, TypeError
    with pytest.raises(TypeError):
        @accepts(int, (int, float))
        def dummy_fun(arg1, arg2):
            return arg1+arg2
        dummy_fun(1, 'a String')

    #   provide a wrong type to the decorator call, TypeError
    with pytest.raises(TypeError):
        @accepts(int, 5)
        def dummy_fun(arg1, arg2):
            return arg1+arg2
        dummy_fun(1, 5)

    #   provide the type's name as string to the decorator call, TypeError
    with pytest.raises(TypeError):
        @accepts(int, 'int')
        def dummy_fun(arg1, arg2):
            return arg1+arg2
        dummy_fun(1, 5)
