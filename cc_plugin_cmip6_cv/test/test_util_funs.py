from cc_plugin_cmip6_cv.util import is_json_cv, compare_json_cv_versions, \
        isinstance_recursive_tuple, is_dir_locked, lock_dir, unlock_dir, \
        download_file, update_needed, update_cmip6_json_cv, update_json_cv, \
        update_performed, data_directory_collection
import cc_plugin_cmip6_cv.util as util
import pytest
import os
import datetime
import inspect
import appdirs

__current_dir__ = os.path.abspath(os.path.dirname(__file__))
__lock_test_dir__ = __current_dir__+'/tmp_test_lock'
__data_url__ = 'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master'

__lock_file__ = '.locked'
__last_update_file__ = '.last_update'

__update_period__ = datetime.timedelta(days=7)


# TODO: test special case: `is instance` => `type`; think about structure ...
def prepost_test_dir(test_dir):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # PREPARATION
            # check if dir/file exists
            if os.path.exists(test_dir):
                # check if file exists with dir name;
                # if yes, remove it
                if os.path.isfile(test_dir):
                    os.remove(test_dir)
                # check if dir exists;
                # if yes, remove it
                if os.path.isdir(test_dir):
                    remove_recursive(test_dir)
            # create test directory
            os.makedirs(test_dir)

            # CALL FUNCTION
            output = func(*args, **kwargs)

            # FINALIZE
            os.rmdir(test_dir)

            # return function's output
            return output
        return wrapper
    return decorator


def remove_recursive(target_dir):
    # check if dir/file exists
    if os.path.exists(target_dir):
        # check if file exists with dir name;
        # if yes, remove it
        if os.path.isfile(target_dir):
            os.remove(target_dir)
        # check if dir exists;
        # if yes, remove it
        if os.path.isdir(target_dir):
            for elem in os.listdir(target_dir):
                remove_recursive(target_dir+'/'+elem)
            os.rmdir(target_dir)


def test_util_constants():
    # set global module-variables to check
    test_constants = ['__data_url__', '__lock_file__',
                      '__last_update_file__', '__update_period__']
    # get global module-variables of module util
    util_members = dict(inspect.getmembers(util))

    # iterate global variables and compare them
    for const in test_constants:
        assert globals()[const] == util_members[const]


def test_isinstance_recursive_tuple():
    # basic test against isinstance
    assert isinstance(5,   int)   == isinstance_recursive_tuple(5,   int)    # True
    assert isinstance(5.2, int)   == isinstance_recursive_tuple(5.2, int)    # False
    assert isinstance(5.2, float) == isinstance_recursive_tuple(5.2, float)  # True
    assert isinstance(5.2, str)   == isinstance_recursive_tuple(5.2, str)    # False
    assert isinstance("v", str)   == isinstance_recursive_tuple("v", str)    # False
    assert isinstance(int, type)  == isinstance_recursive_tuple(int, type)   # True
    assert isinstance(5.2, type)  == isinstance_recursive_tuple(5.2, type)   # False

    # more tests against isinstance
    assert isinstance(5,   (int, float)) == isinstance_recursive_tuple(5,   (int, float))  # True
    assert isinstance(5,   (float, int)) == isinstance_recursive_tuple(5,   (float, int))  # True
    assert isinstance(5.2, (int, str))   == isinstance_recursive_tuple(5.2, (int, str))    # False
    assert isinstance(5.2, (int, float)) == isinstance_recursive_tuple(5.2, (int, float))  # True
    assert isinstance(5.2, (int, (float, str))) == isinstance_recursive_tuple(5.2, (int, (float, str)))  # True

    # test new features not existing in `isinstance`
    assert isinstance_recursive_tuple((5, 4), int)                # True
    assert isinstance_recursive_tuple((int, str), type)           # True
    assert isinstance_recursive_tuple((int, (str, float)), type)  # True
    assert not isinstance_recursive_tuple((int, 77.3), type)      # False
    assert not isinstance_recursive_tuple((int, 77.3), float)     # False
    assert not isinstance_recursive_tuple(('int', 77.3), type)    # False

    # throw some errors if isinstance throws them as well
    with pytest.raises(TypeError):
        isinstance_recursive_tuple(5.2, 5)
    with pytest.raises(TypeError):
        isinstance_recursive_tuple(5.2, (5, float))
    
    # isinstance(5.2, (float, 5)) does not throw a type error.
    # Hence, isinstance_recursive_tuple(5.2, (float, 5)) also should not throw
    # a type error.
    try:
        isinstance(5.2, (float, 5))
        assert isinstance(5.2,
                          (float, 5)) == isinstance_recursive_tuple(5.2,
                                                                    (float, 5))
    except TypeError:
        with pytest.raises(TypeError):
            isinstance_recursive_tuple(5.2, (float, 5))


# @pytest.mark.skip(reason="test function not implemented yet")
def test_data_directory_collection():

    # some default variables
    appname = 'test_app'
    appauthor = 'test_creator'
    user_download_directory = appdirs.user_data_dir(appname, appauthor)
    current_dir_util = os.path.split(__current_dir__)[0]
    fall_back_directory = current_dir_util+'/data'
    ENV_VAR_NAME = 'TEST_ENV_VAR'
    ENV_VAR_VAL_GOOD = current_dir_util
    ENV_VAR_VAL_BAD = current_dir_util+'/a/b/c/d/e/f/g/h/i/j'

    # check with no environement variable set
    my_data_dir_col = data_directory_collection(ENV_VAR_NAME, appname,
                                                appauthor)
    assert my_data_dir_col.__data_dir__ == user_download_directory
    assert my_data_dir_col.__do_update__
    assert my_data_dir_col.__fallback_dir__ == fall_back_directory

    # check with existing environment variable and existing directory
    os.environ[ENV_VAR_NAME] = ENV_VAR_VAL_GOOD
    my_data_dir_col = data_directory_collection(ENV_VAR_NAME, appname,
                                                appauthor)
    assert my_data_dir_col.__data_dir__ == ENV_VAR_VAL_GOOD
    assert not my_data_dir_col.__do_update__

    # check with existing environment variable and non-existing directory
    os.environ[ENV_VAR_NAME] = ENV_VAR_VAL_BAD
    my_data_dir_col = data_directory_collection(ENV_VAR_NAME, appname,
                                                appauthor)
    assert my_data_dir_col.__data_dir__ == user_download_directory
    assert my_data_dir_col.__do_update__

    # unset env var
    os.environ.unsetenv(ENV_VAR_NAME)


# @pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_lock_dir():
    # lock testing file
    lock_test_file = __lock_test_dir__+'/'+__lock_file__

    # dir should not be locked; locking possible
    assert lock_dir(__lock_test_dir__)
    # check if lock file exists
    assert os.path.isfile(lock_test_file)
    # calling lock_dir() again on locked dir should yield `False`
    assert not lock_dir(__lock_test_dir__)
    # remove lock file and try to lock again
    os.remove(lock_test_file)
    assert lock_dir(__lock_test_dir__)

    # remove test file
    os.remove(lock_test_file)

    # create a directory with name of the lock file
    os.makedirs(lock_test_file)
    with pytest.raises(IsADirectoryError):
        lock_dir(__lock_test_dir__)

    # remove directory with name of lock file and try to lock again
    os.rmdir(lock_test_file)
    assert lock_dir(__lock_test_dir__)
    # remove test file
    os.remove(lock_test_file)


# @pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_unlock_dir():
    # lock testing file
    lock_test_file = __lock_test_dir__+'/'+__lock_file__

    # create lock file manually
    handle_lock_file = open(lock_test_file, 'w')
    # NOTE: keep for debugging
    iostat = handle_lock_file.write(datetime.date.today().strftime('%Y-%m-%d'))
    handle_lock_file.close()

    # check if test lock file really exists
    assert os.path.isfile(lock_test_file)

    # should return true and remove the lock file
    assert unlock_dir(__lock_test_dir__)
    # check if lock file really was removed
    assert not os.path.isfile(lock_test_file)
    # calling unlock_dir() on non-locked directory should also lead true
    assert unlock_dir(__lock_test_dir__)

    # create a directory with name of the lock file
    os.makedirs(lock_test_file)
    with pytest.raises(IsADirectoryError):
        unlock_dir(__lock_test_dir__)

    # remove directory with name of lock file and try to unlock again
    os.rmdir(lock_test_file)
    assert unlock_dir(__lock_test_dir__)


# @pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_is_dir_locked():
    # lock testing file
    lock_test_file = __lock_test_dir__+'/'+__lock_file__

    # check if locked (should not be locked)
    assert not is_dir_locked(__lock_test_dir__)

    # create a lock file and check if dir is locked now
    # create lock file
    handle_lock_file = open(lock_test_file, 'w')
    # NOTE: keep for debugging
    iostat = handle_lock_file.write(datetime.date.today().strftime('%Y-%m-%d'))
    handle_lock_file.close()
    # check lock status
    assert is_dir_locked(__lock_test_dir__)
    # remove file
    os.remove(lock_test_file)
    # create a directory with name of the lock file; check lock again
    os.makedirs(lock_test_file)
    assert is_dir_locked(__lock_test_dir__)
    # remove directory with name of lock file and see lock status again
    os.rmdir(lock_test_file)
    assert not is_dir_locked(__lock_test_dir__)


@pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_download_file():
    # TODO: implement
    pass


@pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_update_needed():
    # TODO: implement
    pass


@pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_update_performed():
    # TODO: implement
    pass


@pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_update_json_cv():
    # TODO: implement
    pass


@pytest.mark.skip(reason="test function not implemented yet")
@prepost_test_dir(__lock_test_dir__)
def test_update_cmip6_json_cv():
    # TODO: implement
    pass


def test_is_json_cv():
    path = "cc_plugin_cmip6_cv/test/data"
    # True: correct CVs in correct JSON files
    assert is_json_cv(path+"/CMIP6_nominal_resolution.json")
    assert is_json_cv(path+"/CMIP6_institution_id.json")
    assert is_json_cv(path+"/CMIP6_test_two_cvs.json")
    # False: incorrect JSON files and bad CVs in correct JSON files
    assert not is_json_cv(path+"/CMIP6_test_fail01.json")
    assert not is_json_cv(path+"/CMIP6_test_fail02.json")
    assert not is_json_cv(path+"/CMIP6_test_fail03.json")
    assert not is_json_cv(path+"/CMIP6_test_fail04.txt")
    assert not is_json_cv(path+"/CMIP6_test_fail05.txt")
    assert not is_json_cv(path+"/CMIP6_test_fail06.json")
    assert not is_json_cv(path+"/not_an_existing_file.json")
    # True: provide names of CVs that via `cv_name` that actually exist in the
    #        provided CVs
    assert is_json_cv(path+"/CMIP6_institution_id.json",
                      cv_name="institution_id")
    assert is_json_cv(path+"/CMIP6_institution_id.json",
                      cv_name=["institution_id"])
    assert is_json_cv(path+"/CMIP6_test_two_cvs.json",
                      cv_name="institution_id")
    assert is_json_cv(path+"/CMIP6_test_two_cvs.json",
                      cv_name=["institution_id"])
    assert is_json_cv(path+"/CMIP6_test_two_cvs.json",
                      cv_name=["institution_id", "nominal_resolution"])
    # False: provide names of CVs that do not exist in provided CVs or provide
    #         bad values for `cv_name`
    assert not is_json_cv(path+"/CMIP6_institution_id.json",
                          cv_name="not_existing_cv_name")
    assert not is_json_cv(path+"/CMIP6_institution_id.json",
                          cv_name=["not_existing_cv_name"])
    assert not is_json_cv(path+"/CMIP6_institution_id.json",
                          cv_name=["institution_id", "not_existing_cv_name"])
    assert not is_json_cv(path+"/CMIP6_test_two_cvs.json",
                          cv_name=["institution_id", "not_existing_cv_name"])
    assert not is_json_cv(path+"/CMIP6_institution_id.json",
                          cv_name="version_metadata")
    assert not is_json_cv(path+"/CMIP6_institution_id.json",
                          cv_name=["institution_id", "version_metadata"])
    # False: provide empty file name
    assert not is_json_cv("")
    # ValueError: provide wrong types for the arguments
    with pytest.raises(ValueError):
        is_json_cv(5)
    with pytest.raises(ValueError):
        is_json_cv(path+"/CMIP6_nominal_resolution.json", verbose=77)


def test_compare_json_cv_versions():
    path = "cc_plugin_cmip6_cv/test/data"
    # return file0:
    file0 = path+"/CMIP6_nominal_resolution.json"
    #   files provided (file0 == file1)
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution.json")
    #   same file version but different files
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_same_version.json")
    #   second version number higher
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_lower_version_a.json")
    #   second version number higher; provide `verbose = False` explicitely
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_lower_version_a.json", verbose=False)
    #   first version number higher, second version number lower
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_lower_version_b.json")
    #   third version number higher, fourth version number lower
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_lower_version_c.json")
    #   third version number higher but left most digit is lower (see if really integer are compared)
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_nominal_resolution_lower_version_d.json")
    #   file1 points to bad file
    assert file0 == compare_json_cv_versions(file0, path+"/CMIP6_test_fail01.json")
    #   file1 points to non-existing file
    assert file0 == compare_json_cv_versions(file0, path+"/not_an_existing_file.json")
    #   file1 is empty string
    assert file0 == compare_json_cv_versions(file0, "")

    # return file1:
    file1 = path+"/CMIP6_nominal_resolution.json"
    #   second version number lower
    assert file1 == compare_json_cv_versions(path+"/CMIP6_nominal_resolution_lower_version_a.json", file1)
    #   second version number lower; provide `verbose = False` explicitely
    assert file1 == compare_json_cv_versions(path+"/CMIP6_nominal_resolution_lower_version_a.json", file1, verbose = False)
    #   first version number lower, second version number higher
    assert file1 == compare_json_cv_versions(path+"/CMIP6_nominal_resolution_lower_version_b.json", file1)
    #   third version number lower, fourth version number higher
    assert file1 == compare_json_cv_versions(path+"/CMIP6_nominal_resolution_lower_version_c.json", file1)
    #   third version number lower but left most digit is higher (see if really integer are compared)
    assert file1 == compare_json_cv_versions(path+"/CMIP6_nominal_resolution_lower_version_d.json", file1)
    #   file0 points to bad file
    assert file1 == compare_json_cv_versions(path+"/CMIP6_test_fail01.json", file1)
    #   file0 points to non-existing file
    assert file1 == compare_json_cv_versions(path+"/not_an_existing_file.json", file1)
    #   file0 is empty string
    assert file1 == compare_json_cv_versions("", file1)

    # return ""; empty string
    #   file0 and file1 are empty strings
    assert "" == compare_json_cv_versions("", "")
    #   file0 is empty string; file1 is bad file
    assert "" == compare_json_cv_versions("", path+"/CMIP6_test_fail01.json")
    #   file0 is bad file; file1 is empty string
    assert "" == compare_json_cv_versions(path+"/CMIP6_test_fail01.json", "")
    #   file0 and file1 are different bad files
    assert "" == compare_json_cv_versions(path+"/CMIP6_test_fail01.json", path+"/CMIP6_test_fail02.json")
    #   file0 and file1 are identical bad files
    assert "" == compare_json_cv_versions(path+"/CMIP6_test_fail01.json", path+"/CMIP6_test_fail01.json")

    # test wrong input: ValueError
    with pytest.raises(TypeError):
        compare_json_cv_versions(path+"/CMIP6_nominal_resolution.json", 5)
    with pytest.raises(TypeError):
        compare_json_cv_versions(77.3, path+"/CMIP6_nominal_resolution.json")
    with pytest.raises(TypeError):
        compare_json_cv_versions(path+"/CMIP6_nominal_resolution.json", path+"/CMIP6_nominal_resolution_lower_version_a.json", verbose = "Hallo!")


@pytest.mark.skip(reason="test function not implemented yet")
def test_compare_str_cv_versions():
    # TODO: implement test
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_compare_dict_cv_versions():
    # TODO: implement test
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_read_cmip6_json_cv():
    # TODO: implement test
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_read_json_cv():
    # TODO: implement test
    pass