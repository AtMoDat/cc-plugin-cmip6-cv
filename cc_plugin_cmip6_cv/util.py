import json
import requests
import functools
import sys
import os
import inspect
import time
import shutil
import datetime
import appdirs
import warnings

# ~~~~~~~~~~~~~~ global variables ~~~~~~~~~~~~~~
# some directories and URLs
__current_dir__ = os.path.abspath(os.path.dirname(__file__))
__data_url__ = 'https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master'
# some files
__lock_file__ = '.locked'
__last_update_file__ = '.last_update'
# we test for curr_date >= last_date + __update_period__
__update_period__ = datetime.timedelta(days=7)


# ~~~~~~~~~~~~~~ helper functions ~~~~~~~~~~~~~~
def isinstance_recursive_tuple(arg, type2check):

    # check if `arg` is of the type provided by `type2check`
    if(isinstance(arg, type2check)):
        return True

    if(isinstance(arg, tuple)):
        if(not any([not isinstance_recursive_tuple(a, type2check)
                    for a in arg])):
            return True

    return False


# ~~~~~~~~~~~~~~ DECORATORS ~~~~~~~~~~~~~~
def accepts(*types):
    """
    TODO

    Basic idea for this decorator comes from:
    * source: https://stackoverflow.com/a/15300191/4612235
    * user: jfs (https://stackoverflow.com/users/4279/jfs)

    TODO: parameters and return

    """
    my_name = sys._getframe().f_code.co_name

    def decorator(func):
        # get argument names and count them
        arg_names = [param.name
                     for param in inspect.signature(func).parameters.values()]
        nargs = len(arg_names)
        # check if same number of types and arguments
        if(len(types) != nargs):
            raise RuntimeError("cv_tools.%s:: number of arguments and types"
                               " to test differ." % my_name)
        if(any([not isinstance_recursive_tuple(t, (type, type(None)))
                for t in types])):
            raise TypeError("cv_tools.%s:: only arguments of type `type` are" +
                            " allowed for this decorator")
        # build a dictionary of arguments names and types
        arg_types = dict(zip(arg_names, types))

        # the actual wrapper
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # collect args and kwargs in one dict
            new_kwargs = dict(zip(arg_names[0:len(args)], args))
            new_kwargs.update(kwargs)

            # iterate argument names arguments
            for (arg_name, arg_val) in new_kwargs.items():
                # get required argument type for this argument
                req_arg_type = arg_types[arg_name]
                # check if `type` was set to `None` => do not test
                if(req_arg_type is None):
                    continue
                if(not isinstance(arg_val, req_arg_type)):
                    # check whether `req_arg_type` is type `type` or `tuple`
                    #   `req_arg_type` is `type`
                    if(isinstance(req_arg_type, type)):
                        raise TypeError("cv_tools."+func.__name__+":: " +
                                        "argument "+arg_name+" does not " +
                                        "match type `"+req_arg_type.__name__ +
                                        "`")
                    #   `t` is tuple
                    if(isinstance(req_arg_type, tuple)):
                        #   check if all values in the tuple are of type `type`
                        if (not any([not isinstance(t, type)
                                     for t in req_arg_type])):
                            raise TypeError("cv_tools.%s:: argument %r does" +
                                            " not match type (%r)" +
                                            "" % (func.__name__,
                                                  arg_name,
                                                  ', '.join([t.__name__
                                                             for t
                                                             in req_arg_type]
                                                            )))
                    #   `t` is (neither `type` nor `tuple`)
                    #    or (`tuple` but not all elements in `tuple`
                    #            are `types`)
                    try:
                        raise TypeError("cv_tools.%s:: a type provided to" +
                                        " decorator has strange type: %r " +
                                        "" % (func.__name__,
                                              req_arg_type.__name__))
                    except AttributeError:
                        raise TypeError("cv_tools.%s:: a type provided to" +
                                        " decorator has strange type" +
                                        "" % (func.__name__))
            return func(*args, **kwargs)
        return wrapper
    return decorator


# a helper class
class data_directory_collection(object):

    def __init__(self, envvar_dirname, appname, appauthor):

        # initialize variables
        self.__fallback_dir__ = __current_dir__+'/data'
        self.__data_dir__ = None
        self.__do_update__ = False

        # check if user has set an env ver `envvar_dirname`
        if (os.environ.get(envvar_dirname) and
                os.path.exists(os.environ[envvar_dirname])):
            # get value of env var
            self.__data_dir__ = os.environ[envvar_dirname]
            # do no update from online resource
            self.__do_update__ = False
        else:
            # set data_dir_2 to home dir; via appdirs
            self.__data_dir__ = appdirs.user_data_dir(appname, appauthor)
            # do update from online resource
            self.__do_update__ = True

            # check if __data_dir__ exists; if not: create
            if not os.path.exists(self.__data_dir__):
                try:
                    os.makedirs(self.__data_dir__)
                except PermissionError:
                    self.__data_dir__ = self.__fallback_dir__
                    self.__do_update__ = False
                except FileExistsError:
                    pass


@accepts((str, list), data_directory_collection, bool)
def update_cmip6_json_cv(cv_name, dst_dir_coll, force_update=False):

    # get function's name
    my_name = sys._getframe().f_code.co_name

    # construct file name(s)
    if(isinstance(cv_name, list)):
        # ~~~ set names ~~~
        # TODO: consider to remove duplicates
        # construct file names and ...
        file_name = ['CMIP6_'+n+'.json' for n in cv_name if isinstance(n, str)]

    else:
        # if `cv_name` is not of type string, return empty dict
        if (not isinstance(cv_name, str)):
            raise TypeError('util.'+my_name+':: argument cv_name of bad type')

        # set name
        file_name = ['CMIP6_'+cv_name+'.json']

    # we only proceed if `file_name` is not empty
    if (len(file_name) > 0):
        return update_json_cv(file_name, __data_url__, dst_dir_coll,
                              force_update)

    return []


@accepts(str)
def is_dir_locked(some_dir):
    return os.path.exists(some_dir+'/'+__lock_file__)


@accepts(str)
def lock_dir(some_dir):
    # get function's name
    my_name = sys._getframe().f_code.co_name
    # construct path of lock file
    lock_path = some_dir+'/'+__lock_file__
    # get todays date and convert into string
    str_today = datetime.date.today().strftime('%Y-%m-%d')

    if (is_dir_locked(some_dir)):
        if os.path.isfile(lock_path):
            return False
        else:
            raise IsADirectoryError('utils.'+my_name+':: a directory with ' +
                                    'name of the lock file exists; please ' +
                                    'remove manually: '+lock_path)
    else:
        handle_lock_file = open(lock_path, 'w')
        # NOTE: keep this for debugging
        iostat = handle_lock_file.write(str_today)
        handle_lock_file.close()
        return True


@accepts(str)
def unlock_dir(some_dir):
    # get function's name
    my_name = sys._getframe().f_code.co_name
    # if lock exists, remove lock file
    if (is_dir_locked(some_dir)):
        if os.path.isfile(some_dir+'/'+__lock_file__):
            os.remove(some_dir+'/'+__lock_file__)
        else:
            raise IsADirectoryError('utils.' + my_name + ':: a directory wit' +
                                    'h name of the lock file exists; please ' +
                                    'remove manually: ' + some_dir + '/' +
                                    __lock_file__)
    # check if file really was removed
    if (not is_dir_locked(some_dir)):
        return True
    # lock does still exist
    return False


@accepts(str)
def update_needed(some_dir):
    """
    Checks if data/cv files in directory `some_dir` need to be updated.

    The checking is done by comparing the date of the last update with today's
    date. If no update was performed in the timespan given by 
    `__update_period__`, which is hard-coded and defined in this module, then
    `True` is returned. Currently, it is set to seven days. The date of the
    last updated is stored in a file located in the directory `some_dir`.

    The date in the update file is formatted as 'YYYY-MM-DD'. Other formats do
    not work. If another format or content is provided, the file is ignored and
    '1900-01-01' is assumed as last update date.

    If `some_dir` does not exist, an OSError is thrown. If a directory with the
    same name than the update status file exists in `some_dir` instead of the
    file then an IsADirectoryError is thrown.

    @parameter some_dir str directory in which data should be updated
    @return bool True if update is needed and False otherwise
    """
    # if update period is 0 or negative, we return True
    if __update_period__ <= datetime.timedelta():
        return True
    # get function's name
    my_name = sys._getframe().f_code.co_name
    # set path of update file
    last_update_path = some_dir+'/'+__last_update_file__
    # get todays date
    todays_date = datetime.date.today()

    if not os.path.exists(some_dir):
        raise OSError('util.'+my_name+':: provided directory `' + some_dir +
                      '` does not exist.')

    if os.path.exists(last_update_path):
        if os.path.isdir(last_update_path):
            raise IsADirectoryError('util.'+my_name+':: update status file ' +
                                    'is a directory: '+last_update_path)
        # open last-update-file and get date of last update
        handle_update_file = open(last_update_path)
        str_last_update_date = handle_update_file.readline()
        handle_update_file.close()
        try:
            # convert last-update-date-string into datetime.date
            last_update_date = datetime.datetime.strptime(str_last_update_date,
                                                          '%Y-%m-%d').date()
        except ValueError:
            # If conversion not possible provide warning and set last update
            # date to 1900/01/01.
            last_update_date = datetime.datetime.strptime('1900-01-01',
                                                          '%Y-%m-%d').date()
            warnings.warn('util.' + my_name + ':: cannot convert date read f' +
                          'rom update status file into datetime object; assu' +
                          'ming that update has to be performed; value: ' +
                          str_last_update_date,
                          RuntimeWarning)

        # compare current date and last-update-date
        if todays_date >= last_update_date + __update_period__:
            return True
        else:
            return False
    else:
        # if no update status file exists: return True => need update
        return True


@accepts(str)
def update_performed(some_dir):
    """
    Updates or creates an update-status-file. If a directory exists in place of
    the file two write, an `IsADirectoryError` is thrown. If something, which
    is not a file or directory is in place, an OSError is thrown. If the
    directory `some_dir` does not exist, a `OSError` is thrown.

    @param some_dir str name of the directory in which the update-status-file
                        is to be located
    @return bool True if `update_performed` was run successfully and update-
                    status-file was properly written; otherwise, an error
                    should have been thrown
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name
    # set path of update file
    last_update_path = some_dir+'/'+__last_update_file__
    # get todays date
    str_todays_date = datetime.date.today().strftime('%Y-%m-%d')

    if not os.path.exists(some_dir):
        raise OSError('util.'+my_name+':: provided directory `' + some_dir +
                      '` does not exist.')

    # if file/directory with file name does exist, try to remove it
    if os.path.exists(last_update_path):
        if os.path.isdir(last_update_path):
            raise IsADirectoryError('util.'+my_name+':: update status file ' +
                                    'is a directory: '+last_update_path)
        if os.path.isfile(last_update_path):
            os.remove(last_update_path)
        else:
            raise OSError('util.'+my_name+':: something exists at the ' +
                          'location of ')

    # write the update-date-file
    handle_update_file = open(last_update_path, 'w')
    # NOTE: keep this for debugging
    iostat = handle_update_file.write(str_todays_date)
    handle_update_file.close()

    return True


@accepts(str, str, bool)
def download_file(src_file, dst_file, overwrite=True):
    """
    Downloads `src_file` and saves it as `dst_file`.

    Downloads `src_file` and saves it as `dst_file`. If `dst_file` does exist,
    it is overwritten -- except if `overwrite` is set to `False`. If either the
    webserver is not available or the webserver is available but provides a 
    HTTP error code, then no file is written and `None` is returned. Otherwise,
    if the download was successful, the value of `dst_file` is returned.

    @param src_file str download url of the file to obtain
    @param dst_file str destination path (directory + file name) where to save
                        the downloaded file
    @param overwrite bool choose to overwrite `dst_file` if it already exists
                          [True]
    @return `None` or value of `dst_file`; value `dst_file` if download
                                           successful and `None` otherwise
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    if (os.path.isfile(dst_file) and not overwrite):
        raise OSError('util.' + my_name + ': Destination file `dst_file` doe' +
                      's already exist. Set `overwrite` to `True` to overwri' +
                      'te it.')

    try:
        # send request
        r = requests.get(src_file, allow_redirects=True)
        # check if status code indicates successful download
        if r.status_code == requests.codes.ok:
            # write file
            open(dst_file, mode='wb').write(r.content)
            # if file exists, return file name
            if os.path.isfile(dst_file):
                return dst_file
            warnings.warn('util.' + my_name + ':: file could not be download' +
                          'ed and saved for unknown reason; source url: ' +
                          src_file + '; destination file: ' + dst_file, 
                          RuntimeWarning)
        else:
            warnings.warn('util.' + my_name + ':: file could not be download' +
                          'ed; HTTP status code: ' + str(r.status_code) + ';' +
                          ' source url: ' + src_file,
                          RuntimeWarning)
    except requests.ConnectionError:
        warnings.warn('util.' + my_name + ':: connection could not be establ' +
                      'ished to download file: ' + src_file, RuntimeWarning)

    # something went wrong ...
    return None


@accepts((str, list), str, data_directory_collection, bool)
def update_json_cv(file_name, src_url, dst_dir_coll, force_update=False):

    # get function's name
    my_name = sys._getframe().f_code.co_name

    # set target diretory
    dst_dir = dst_dir_coll.__data_dir__

    # construct path for input, temp and output
    if isinstance(file_name, str):
        src_files = [src_url+'/'+file_name]
        tmp_files = [dst_dir+'/'+'tmp.'+file_name]
        dst_files = [dst_dir+'/'+file_name]
    if isinstance(file_name, list):
        if any([not isinstance(n, str) for n in file_name]):
            raise TypeError('util.'+my_name+':: `file_name` bad type')
        src_files = [src_url+'/'+n for n in file_name]
        tmp_files = [dst_dir+'/'+'tmp.'+n for n in file_name]
        dst_files = [dst_dir+'/'+n for n in file_name]

    # lock directory for other instances of this
    # try this 20 times and wait 2 seconds after each try
    for i in range(0, 19):
        if lock_dir(dst_dir):
            break
        time.sleep(2)

    if force_update:
        do_update = True
    elif not dst_dir_coll.__do_update__:
        # If dst_dir_coll tells us not to update,
        # then we don't do it
        # except if we are forced (`if` above)
        do_update = False
    else:
        do_update = update_needed(dst_dir)

    for src_file, tmp_file, dst_file in zip(src_files, tmp_files, dst_files):
        if ((not os.path.isfile(dst_file)) or do_update):
            # download file
            if tmp_file == download_file(src_file, tmp_file):
                # check if existing file actually is a CMIP6 JSON CV file
                if not is_json_cv(tmp_file):
                    # if not, remove downloaded file and continue to next file
                    os.remove(tmp_file)
                    continue
                # check if existing file is newer or equal
                if dst_file == compare_json_cv_versions(dst_file, tmp_file):
                    # if yes, remove downloaded file and continue to next file
                    os.remove(tmp_file)
                    continue
                # If we arrive here, the tmp_file has a higher version than
                # dst_file or the dst_file does not exist.
                shutil.move(tmp_file, dst_file)
            else:
                warnings.warn('util.'+my_name+':: new version of file ' +
                              os.path.basename(dst_file) + ' could not be do' +
                              'wnloaded; using old version;', RuntimeWarning)

    # update the update information file
    update_performed(dst_dir)

    # unlock dir
    if not unlock_dir(dst_dir):
        warnings.warn('util.'+my_name+':: lock could not be removed for ' +
                      'unknown reason', RuntimeWarning)

    return dst_files


def is_json_cv(file, cv_name="", verbose=False):
    """
    Returns a boolean indicating whether the provided file is a valid
    JSON Controled Vocabulary file as used in CMIP6.

    @param file: string representing the path of a CMIP6 CV json file
    @param cv_name: string or list of strings (optional) containing names of
                    CVs that schould be checked to exist in the JSON file; if
                    empty string, no names are tested [""]
    @param verbose: boolean (optional) to switch verbose mode on and off
                    [off/False]
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    # NOTE: If we encounter that `file` does not contain a valid
    #       CMIP6 CV, we directly leave this function via
    #       `return False`. If we did not leave this function
    #       until its end, then everything is fine and we
    #       `return True`.

    # check if `file` has correct variable type
    if (not isinstance(file, str)):
        raise ValueError('util.'+my_name+':: provided argument `file` has to' +
                         ' be of type `str` but is of type ' +
                         type(file).__name__)

    # check if `file` does not contain an empty string
    if (len(file) == 0):
        if verbose:
            print('util.'+my_name+':: the argument `file` has to be an non-' +
                  'empty string')
        return False

    # check if `verbose` has correct variable type
    if (not isinstance(verbose, bool)):
        raise ValueError('util.'+my_name+':: provided argument `verbose` has' +
                         ' to be of type `bool` but is of type ' +
                         type(verbose).__name__)

    # try to open the json file
    try:
        with open(file) as json_file:
            cv = json.load(json_file)
    except FileNotFoundError:
        # file does not exist at all
        if verbose:
            print('util.'+my_name+':: JSON does not exist: '+file)
        return False
    except json.JSONDecodeError:
        # file exists but is not json file
        if verbose:
            print('util.'+my_name+':: File appears not to be a JSON file: ' +
                  file+'. Printing first line of the file: ("> " prepended)')
            with open(file) as file:
                print('> '+file.readline().strip()+'\n')
        return False

    # Check if size of content of JSON file is reasonable.
    # We need two keys at least:
    # - one key containing the CV
    # - one key holding the version metadata
    # There might be more than one key hosting CVs
    # (one extra key per extra CV).
    if (len(cv) < 2):
        if verbose:
            print('util.'+my_name+':: File is JSON file but contains not ' +
                  'valid CV: '+file+'. A JSON CV file has to contain at ' +
                  'least two keys on the top level.')
            print('             One key ("version_metadata") has to host the' +
                  'metadata and the ')
            print('             other(s) has/have to contain the actual CVs ' +
                  '(one CV per top-level')
            print('             key; the name of the key equal to the CV-' +
                  'name).')
        return False

    # Check if size of content of JSON file is reasonable.
    # We need two keys at least:
    # - one key containing the CV
    # - one key holding the version metadata
    # The latter key is named "version_metadata"
    if ('version_metadata' not in cv.keys()):
        if verbose:
            print('util.' + my_name + ':: The top-level key "version_metadat' +
                  'a" is missing in the JSON file.')
            print('             File: '+file)
        return False

    # Check name(s) of the provided CV(s) if they are provided
    # by the user.
    if (len(cv_name) > 0):
        if verbose:
            print('util.'+my_name+':: Checking the CV(s) name(s)')
        if (not (isinstance(cv_name, str) or isinstance(cv_name, list))):
            if verbose:
                print('util.' + my_name + ':: The provided argument "cv_name' +
                      '" has to be of type string or list.')
                print('             Instead, it is of type ' +
                      type(cv_name).__name__)
            return False
        if (isinstance(cv_name, str)):
            # if we got a CV-name as string ...
            if ('version_metadata' == cv_name):
                if verbose:
                    print('util.' + my_name + ':: "version_metadata" is not ' +
                          'a valid name for a CV.')
                return False
            if (cv_name not in cv.keys()):
                if verbose:
                    print('util.' + my_name + ':: The loaded JSON file does ' +
                          'not hold a CV with the user-provided')
                    print('             name. File: '+file)
                return False
        if (isinstance(cv_name, list)):
            # if we got a list of CV-names ...
            if ('version_metadata' in cv_name):
                if verbose:
                    print('util.' + my_name + ':: "version_metadata" is not ' +
                          'a valid name for a CV.')
                return False
            if (any([not isinstance(x, str) for x in cv_name])):
                # ... but the list does not contain only strings
                if verbose:
                    print('util.' + my_name + ':: The provided argument "cv_' +
                          'name" is a list and holds at least')
                    print('             one non-string elemt. However, all e' +
                          'lements of "cv_name" have')
                    print('             to be strings, if "cv_name" is a lis' +
                          't.')
                return False
            if (any([x not in cv.keys() for x in cv_name])):
                # ... but not all values in cv_name exist in cv.keys()
                # NOTE: keep this for debugging
                bad_names = [y
                             for idx, y in enumerate(cv_name)
                             if [x not in cv.keys() for x in cv_name][idx]]
                # from: https://stackoverflow.com/a/53527901/4612235
                # long version:
                #   cv_name_exists = [x not in cv.keys() for x in cv_name]
                #   bad_name = [y for idx, y in enumerate(cv_name)
                #               if cv_name_exists[idx]]
                if verbose:
                    print('util.' + my_name + ':: Some strings provided in "' +
                          'cv_name" do not exist as keys in ')
                    print('             in the JSON file and, hence, a no va' +
                          'lid CV names of the CV')
                    print('             represented by the JSON file.')
                return False

    # If we did not leave this function up till now, the JSON file can
    # be assumed to contain a proper CMIP6 CV.
    return True


@accepts(str, str, bool)
def compare_str_cv_versions(v0, v1, verbose=False):
    """
    TODO: doc compare_str_cv_versions
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    # version numbers of both files are equal
    if (v0 == v1):
        if verbose:
            print('util.' + my_name + ':: Version numbers of both CVs are id' +
                  'entical (return 0):')
            print('                           cv0:'+v0)
            print('                           cv1:'+v1)
        return 0

    # convert version numbers into integer for later comparison
    #   The version number consists of four numbers separated by a dot each.
    #   Each of the four numbers may consist of one or more digits. Valid
    #   version numbers are (examples):
    #     3.2.41.2
    #     5.9.45.7
    #     6.3.2.77
    version_cv0 = [int(x) for x in v0.split('.')]
    version_cv1 = [int(x) for x in v1.split('.')]

    # compare version numbers
    #   we test all cases explicitely here to make sure not to overlook
    #   special situations!
    # compare first number (major version)
    if (version_cv0[0] > version_cv1[0]):
        if verbose:
            print('util.' + my_name + ':: major version number of CV 0 is hi' +
                  'gher (return 0):')
            print('                           cv0:'+v0)
        return 0
    else:
        if (version_cv0[0] < version_cv1[0]):
            if verbose:
                print('util.' + my_name + ':: major version number of CV 1 i' +
                      's higher (return 1):')
                print('                           cv1:'+v1)
            return 1
        else:
            # compare second number (minor version)
            if (version_cv0[1] > version_cv1[1]):
                if verbose:
                    print('util.' + my_name + ':: minor version number of CV' +
                          ' 0 is higher (return 0):')
                    print('                           cv0:'+v0)
                return 0
            else:
                if (version_cv0[1] < version_cv1[1]):
                    if verbose:
                        print('util.' + my_name + ':: minor version number o' +
                              'f CV 1 is higher (return 1):')
                        print('                           cv1:'+v1)
                    return 1
                else:
                    # compare third number (patch version)
                    if (version_cv0[2] > version_cv1[2]):
                        if verbose:
                            print('util.' + my_name + ':: third version numb' +
                                  'er of CV 0 is higher (return 0):')
                            print('                           cv0:'+v0)
                        return 0
                    else:
                        if (version_cv0[2] < version_cv1[2]):
                            if verbose:
                                print('util.' + my_name + ':: third version ' +
                                      'number of CV 1 is higher (return 1):')
                                print('                           cv1:'+v1)
                            return 1
                        else:
                            # compare fourth number (version for even less
                            #   significant changes)
                            if (version_cv0[3] > version_cv1[3]):
                                if verbose:
                                    print('util.' + my_name + ':: fourth ver' +
                                          'sion number of CV 0 is higher (re' +
                                          'turn 0):')
                                    print('                           cv0:'+v0)
                                return 0
                            else:
                                if (version_cv0[3] < version_cv1[3]):
                                    if verbose:
                                        print('util.' + my_name + ':: fourth' +
                                              ' version number of CV 1 is hi' +
                                              'gher (return 1):')
                                        print('                           cv' +
                                              '1:' + v1)
                                    return 1
                                else:
                                    if verbose:
                                        print('util.' + my_name + ':: All fo' +
                                              'ur version numbers of the CVs' +
                                              ' 0 and 1 are higher identical' +
                                              ' (return 0):')
                                        print('                           cv' +
                                              '0:'+v0)
                                    return 0


@accepts(dict, dict, bool)
def compare_dict_cv_versions(cv0, cv1, verbose=False):
    """
    TODO: doc compare_dict_cv_versions
    """
    return compare_str_cv_versions(cv0['version_metadata']['CV_collection_version'],
                                   cv1['version_metadata']['CV_collection_version'],
                                   verbose)


@accepts(str, str, bool)
def compare_json_cv_versions(file0, file1, verbose=False):
    """
    Compares the version number of two CVs provided as JSON file

    @param file0: string representing the path of a CMIP6 CV json file
    @param file1: string representing the path of a CMIP6 CV json file
    @param verbose: boolean (optional) to switch verbose mode on and off
                        [off/False]
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    # check if `file0` and `file1` have correct variable types
    if (not isinstance(file0, str)):
        raise ValueError('util.' + my_name + ':: provided argument `file0` h' +
                         'as to be of type `str` but is of type ' +
                         type(file0).__name__)
    if (not isinstance(file1, str)):
        raise ValueError('util.' + my_name + ':: provided argument `file1` h' +
                         'as to be of type `str` but is of type ' +
                         type(file1).__name__)
    # we do not test for empty file names

    # check if `verbose` has correct variable type
    if (not isinstance(verbose, bool)):
        raise ValueError('util.' + my_name + ':: provided argument `verbose`' +
                         ' has to be of type `bool` but is of type ' +
                         type(verbose).__name__)

    # if both files are no CVs in JSON files: return empty string
    if(((not is_json_cv(file0)) or (len(file0) == 0))
       and ((not is_json_cv(file1)) or (len(file1) == 0))):
        if verbose:
            print('util.' + my_name + ':: Neither file0 nor file1 are recogn' +
                  'ized as correct CMIP6 CV JSON files:')
            print('                           file0:'+file0)
            print('                           file1:'+file1)
        return ""
        # The `len(fileX) == 0` should be catched by `is_json_cv`.
        # But, to be sure that we will catch this case also in future
        # versions, we test it here.

    # if file1 is not a CV in a JSON file: return file0
    if (is_json_cv(file0) and not is_json_cv(file1)):
        if verbose:
            print('util.' + my_name + ':: file1 is not recognized as correct' +
                  ' CMIP6 CV JSON file (return file0):')
            print('                           file1:'+file1)
        return file0

    # if file0 is not a CV in a JSON file: return file1
    if (is_json_cv(file1) and not is_json_cv(file0)):
        if verbose:
            print('util.' + my_name + ':: file0 is not recognized as correct' +
                  ' CMIP6 CV JSON file (return file1):')
            print('                           file0:'+file0)
        return file1

    # if file0 and file1 are identical strings: return file0
    #   If the file, to which file0 and file1 point, was a bad file
    #   we would have cought this situation already further above.
    if (file0 == file1):
        if verbose:
            print('util.' + my_name + ':: file0 and file1 are identical stri' +
                  'ngs (return file0):'+file0)
        return file0

    # load CVs
    with open(file0) as json_file:
        cv0 = json.load(json_file)
    with open(file1) as json_file:
        cv1 = json.load(json_file)

    cv_compare = compare_dict_cv_versions(cv0, cv1, verbose)
    if (cv_compare == 0):
        return file0
    if (cv_compare == 1):
        return file1

    # for some unforeseen situations
    if verbose:
        print('util.' + my_name + ':: When you arrive at this message it mea' +
              'ns that we did not cover your special case :-( . Please infor' +
              'm the developer.')
    return ""


@accepts((str, list), data_directory_collection)
def read_cmip6_json_cv(cv_name, dst_dir_coll):
    """
    TODO: doc for read_cmip6_json_cv
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    # create a list from cv_name is it is not a list yet
    if isinstance(cv_name, list):
        cv_name_list = cv_name
    elif isinstance(cv_name, str):
        cv_name_list = [cv_name]
    else:
        return {}

    # construct file name(s)
    # TODO: consider to remove duplicates
    # construct file names and ...
    file_name = [dst_dir_coll.__data_dir__+'/CMIP6_'+n+'.json'
                 for n in cv_name if isinstance(n, str)]
    # ... take the CVs for which we need to read files
    cvs_in_files = [n for n in cv_name_list if isinstance(n, str)]

    # if `file_name` is empty, we do not need to do anything; return empty dict
    if (len(file_name) == 0):
        return {}

    # check for correctness
    for n, c, f in zip(range(0, len(cvs_in_files)), cvs_in_files, file_name):

        if not is_json_cv(f):
            # If file does not exist or is no proper cv,
            # replace the directory by the fall back directory
            fnew = f.replace(dst_dir_coll.__data_dir__,
                             dst_dir_coll.__fallback_dir__)
            # Update file path in list
            file_name[n] = fnew
            # Tell it to the user
            warnings.warn('until.'+my_name+':: file for CV ' + c + ' (' +
                          os.path.split(f)[1] + ') does not hold a valid ' +
                          'CMIP6 json CV or does not exists in directory ' +
                          os.path.split(f)[0] + '. Switching to fall-back ' +
                          'directory: ' + os.path.split(fnew)[0],
                          RuntimeWarning)

            if(not is_json_cv(fnew)):
                raise RuntimeError('until.'+my_name+':: file for CV ' + c +
                                   ' (' + os.path.split(f)[1] + ') does not ' +
                                   ' hold a valid CMIP6 json CV or does not ' +
                                   ' exist in directories ' +
                                   os.path.split(f)[0] + ' and ' +
                                   os.path.split(fnew)[0] + '.')

    # call `read_json_cv` and return the output
    return read_json_cv(file_name)


@accepts((str, list))
def read_json_cv(file_name):
    """

    If we ge a list of file names, we store the version information of
    each file and compare them in the end.

    @param file_name str or list of strings
    """
    # get function's name
    my_name = sys._getframe().f_code.co_name

    # distinguish between
    if(isinstance(file_name, list)):
        # case: we got a list of file names
        if(any([not isinstance(f, str) for f in file_name])):
            raise TypeError('util.'+my_name+':: need a `str` or a `list` of ' +
                            '`str` but got a list with something different.')
        cv = {}
        for f in file_name:
            if(not is_json_cv(f)):
                raise RuntimeError('until.'+my_name+':: file does ' +
                                   'not exists or holds no valid json CV' +
                                   f)
            with open(f) as json_file:
                tmp_cv = json.load(json_file)
            tmp_cv['version_metadata'+f] = tmp_cv.pop('version_metadata')
            cv.update(tmp_cv)

    else:
        # case: we got one file name
        if(not is_json_cv(f)):
            raise RuntimeError('until.'+my_name+':: file does ' +
                               'not exists or holds no valid json CV' +
                               file_name)
        with open(file_name) as json_file:
            cv = json.load(json_file)

    # return CV(s)
    return cv
