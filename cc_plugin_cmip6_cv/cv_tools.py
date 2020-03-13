# IMPORTS
import numpy
import functools
import sys
import inspect
import re
from cc_plugin_cmip6_cv.util import isinstance_recursive_tuple, accepts


# ~~~~~~~~~~~~~~ global variables ~~~~~~~~~~~~~~
# structure of each value of `__cmip6_cv_struct_dict__`:
#   [operation, CV_NAME_IMPORT, CV_VALUES, FUN, RECURSIVE]
__cmip6_cv_struct_dict__ = {'activity_id': ['in', 'activity_id', None,
                                            'keys', False],
                            'parent_activity_id': ['in', 'activity_id',
                                                   None, 'keys', False],
                            'experiment_id': ['in', 'experiment_id', None,
                                              'keys', True],
                            'parent_experiment_id': ['in', 'experiment_id',
                                                     None, 'keys', False],
                            'frequency': ['in', 'frequency', None, 'keys',
                                          False],
                            'grid_label': ['in', 'grid_label', None, 'keys',
                                           False],
                            'institution_id': ['in', 'institution_id', None,
                                               'keys', False],
                            'institution': ['in', 'institution_id', None,
                                            'values', False],
                            'license': ['regex', 'license', None, '', False],
                            'nominal_resolution': ['in', 'nominal_resolution',
                                                   None, '', False],
                            'realm': ['in', 'realm', None, 'keys', False],
                            'source_id': ['in', 'source_id', None, 'keys',
                                          True],
                            'parent_source_id': ['in', 'source_id', None,
                                                 'keys', False],
                            'source_type': ['in', 'source_type', None, 'keys',
                                            False],
                            'sub_experiment': ['in', 'sub_experiment_id',
                                               None, 'values', False],
                            'sub_experiment_id': ['in', 'sub_experiment_id',
                                                  None, 'keys', False],
                            'table_id': ['in', 'table_id', None, '', False],
                            'forcing_index': ['isinstance', 'forcing_index',
                                              numpy.int32, '', False],
                            'Conventions': ['contains_all', 'Conventions',
                                            ['CF-', 'CMIP'], '', False]}
__cmip6_cv_ignore__ = ["activity_participation",
                       "additional_allowed_model_components", "cohort",
                       "description", "end_year", "label_extended", "label",
                       "min_number_yrs_per_sim", "model_component",
                       "release_year", "required_model_components",
                       "start_year", "tier"]
__name__version_metadata__ = 'version_metadata'
__content__version_metadata__ = {"CV_collection_modified": str,
                                 "CV_collection_version": str,
                                 "author": str,
                                 "institution_id": str,
                                 "institution_id_CV_modified": str,
                                 "institution_id_CV_note": str,
                                 "previous_commit": str,
                                 "specs_doc": str}
__allowed_types_for_cvs__ = (dict, list, str, int, float, type, tuple,
                             type(None))


# ~~~~~~~~~~~~~~ decorators ~~~~~~~~~~~~~~
def validate_argument_attribute(arg_name__cv_struct):
    """
    TODO

    used sources
    * processing of `**kwargs`:
       * http://www.informit.com/articles/article.aspx?p=2314818
       * https://stackoverflow.com/questions/53128068/keyerror-in-python-kwargs
    * get name of current function
       * https://www.oreilly.com/library/view/python-cookbook/0596001673/ch14s08.html
       * https://stackoverflow.com/q/5067604/4612235
    * analyse arguments to funcitons
       * https://docs.python.org/3/library/inspect.html#inspect.Signature
       * https://www.programcreek.com/python/example/81294/inspect.signature

    """
    # get my name
    my_name = sys._getframe().f_code.co_name

    def decorator(func):

        # `func` got an instance of `cv_structure`. It might be parsed via
        # different arguments. Here, we list the possible argument names.
        # Further below, we iterate all these argument names from left to
        # right. The first listed argument of the type `cv_structure` is
        # used further.
        argument_name_for_cv_structure = (arg_name__cv_struct
                                          if (arg_name__cv_struct
                                              is not None)
                                          else ['cv_struct', 'self'])
        if(isinstance(argument_name_for_cv_structure, str)):
            argument_name_for_cv_structure = [argument_name_for_cv_structure]
        if(not isinstance(argument_name_for_cv_structure, list)):
            raise TypeError('cv_tools.%s:: argument `arg_name__cv_struct` to' +
                            ' decorator `validate_argument_attribute` has to' +
                            ' be of type `str` or `list` filled with `str` ' +
                            'but it is of type `%s`.' %
                            (my_name,
                             type(argument_name_for_cv_structure).__name__))
        # if(any([not isinstance(val, str)
        #         for val in argument_name_for_cv_structure])):
        for val in argument_name_for_cv_structure:
            if not isinstance(val, str):
                raise TypeError('cv_tools.%s:: argument `arg_name__cv_struct' +
                                '` to decorator `validate_argument_attribute' +
                                '` has to be of type `str` or `list` filled ' +
                                'with `str` but it is list filled with `%s`.' %
                                (my_name, type(val).__name__))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # get argument names
            arg_names = [param.name
                         for param
                         in inspect.signature(func).parameters.values()]
            # collect args and kwargs in one dict
            new_kwargs = dict(zip(arg_names[0:len(args)], args))
            new_kwargs.update(kwargs)

            # check if argument `attibute` exists at all in `func`'s call
            if('attribute' not in arg_names):
                raise RuntimeError('cv_tools.'+my_name+':: function without' +
                                   ' argument `attribute` was decorated with' +
                                   ' decorator `validate_argument_attribute`;')
            attribute = new_kwargs['attribute']
            # check if we got an instance of `cv_structure`
            for arg_name in argument_name_for_cv_structure:
                if(arg_name in arg_names):
                    cv_struct = new_kwargs[arg_name]
                    if(isinstance(cv_struct, cv_structure)):
                        break
            else:
                cv_struct = None
                raise RuntimeError('cv_tools.'+my_name+':: function without' +
                                   ' argument holding a `cv_struct` was dec' +
                                   'orated with decorator `validate_argumen' +
                                   't_attribute`; the  argument\'s name has' +
                                   ' to be in this list: ' +
                                   ', '.join(argument_name_for_cv_structure))
            # check if argument `attribute` is of correct type
            if(not isinstance(attribute, str)):
                raise TypeError('cv_struture.'+func.__name__+':: wrong type ' +
                                'of argument `attribute`; need `str` but got' +
                                ' ' + type(attribute).__name__)
            # check if argument `attribute` exists in passed instance of
            #   `cv_structure`
            if(attribute not in cv_struct.keys()):
                raise ValueError('cv_struture.'+func.__name__+':: the value' +
                                 ' of argument `attribute` has to be the' +
                                 ' key/attribute of this instance of' +
                                 ' cv_structure')
            # call the actual function
            return func(*args, **kwargs)

        return wrapper
    return decorator


class cv_structure(dict):

    __allowed_operations__ = {'in': 'in',
                              'not in': 'not_in',
                              'not_in': 'not_in',
                              'notin': 'not_in',
                              'regex': 'regex',
                              'regular expresion': 'regex',
                              'regular_expresion': 'regex',
                              'isinstance': 'isinstance',
                              'is_instance': 'isinstance',
                              'is instance': 'isinstance',
                              'contains any': 'contains_all',
                              'contains_any': 'contains_all',
                              'containsany': 'contains_all',
                              'contains all': 'contains_all',
                              'contains_all': 'contains_all',
                              'containsall': 'contains_all'}
    # NOTE: If this variable is updated, please consider updating the function
    #       `self.convert_cv_prepare_fun` as well.
    __allowed_cv_preproc_funs__ = ['keys', 'dict.keys', 'values',
                                   'dict.values']

    def __init__(self, *args, **kwargs):
        """
        Extended init function by some tests for the more restricted
        structure of `cv_struture` compared to `dict`.
        """
        super().__init__(*args, **kwargs)
        # dict.__init__(self, *args, **kwargs)

        my_name = sys._getframe().f_code.co_name

        # test, whether our input has the structure we want
        for key, value in self.items():
            # check type of definition of cv_structure (should be list)
            if(not isinstance(value, list)):
                raise TypeError('cv_structure.'+my_name+':: bad item;' +
                                ' structure has to be: "key: list of length' +
                                ' 5"; key: '+key)

            # check length of list holding definitino of cv_structure
            if(len(value) != 5):
                raise ValueError('cv_structure.__init__:: bad item; the' +
                                 ' value has to be list of length 5";' +
                                 ' key: ' + key)

            # check 1st value
            if not isinstance(value[0], str):
                raise TypeError('cv_structure.__init__:: The first entry of ' +
                                'a cv_structure definition has to be of type' +
                                ' `str`. This is not the case. The type is ' +
                                type(value[0]).__name__ + '; key: ' + key)
            if not self.is_operation_allowed(value[0]):
                raise ValueError('cv_structure.__init__:: bad value for' +
                                 ' first entry in list in value: TODO, more' +
                                 ' info')
            value[0] = self.convert_operation(value[0])

            # check 2nd value
            if not isinstance(value[1], str):
                raise TypeError('cv_structure.__init__:: The second entry of' +
                                ' a cv_structure definition has to be of typ' +
                                'e `str`. This is not the case. The type is ' +
                                type(value[1]).__name__ + '; key: ' + key)

            # check 3rd value
            if not isinstance(value[2], __allowed_types_for_cvs__):
                raise TypeError('cv_structure.__init__:: The third entry of ' +
                                'a cv_structure definition has to be of one ' +
                                'of the type provided in `cv_tools.__allowed' +
                                '_types_for_cvs__`. This is not the case. Th' +
                                'e type is ' + type(value[2]).__name__ +
                                '; key: ' + key)
            if(value[0] == 'isinstance'
                    and not (isinstance_recursive_tuple(value[2], type)
                             or (value[2] is None))):
                raise TypeError('cv_structure.__init__:: If the first entry ' +
                                'of a cv_structure definition holds the oper' +
                                'ation/string `isinstance`, then the second ' +
                                'entry has to be of type `type` or a tuple o' +
                                'f `type`. This is not the case. The type is' +
                                ' ' + type(value[2]).__name__ + '; key: ' +
                                key)
            # do deeper validation of value[2]; a bit experimental
            if value[2] is not None:
                if validate_structure_of_cvs({'dummy_key': value[2]},
                                             check_version=False,
                                             recursive=True):
                    RuntimeError('cv_structure.__init__:: The third entry of' +
                                 ' this cv_structure definition was consider' +
                                 'ed as a CV (because `is not None`). Howeve' +
                                 'r, it did not succeed a test by function `' +
                                 'cv_tools.validate_structure_of_cvs`. The r' +
                                 'eason for this is not clear. key: ' + key)

            # check 4th value
            if not isinstance(value[3], str):
                raise TypeError('cv_structure.__init__:: The fourth entry of' +
                                ' a cv_structure definition has to be of typ' +
                                'e `str`. This is not the case. The type is ' +
                                type(value[3]).__name__)
            if not self.is_cv_prepare_fun_allowed(value[3]):
                raise ValueError('cv_structure.__init__:: The function (prov' +
                                 'ided as forth entry of the definition of a' +
                                 ' cv_structure) is not in the set of allowe' +
                                 'd functions. Trying to print function name' +
                                 ': ' + self.get_cv_prepare_fun_name(value[3]))

            # check 5th value
            if not isinstance(value[4], (cv_structure, bool)):
                raise TypeError('cv_structure.__init__:: The fifth entry of ' +
                                'a cv_structure definition has to be of type' +
                                ' `bool` or `cv_structure`. This is not the ' +
                                'case. The type is ' +
                                type(value[4]).__name__ + '; key: ' + key)

    def get_attributes_to_check(self):
        return super(cv_structure, self).keys()

    # return names for which no CV exists yet
    def get_cv_names_needed(self):
        return list(set([values[1]
                         for values
                         in self.values() if values[2] is None]))

    @accepts(None, str)
    @validate_argument_attribute('self')
    def get_cv_check_definition(self, attribute):
        # do not return the fourth element
        return self[attribute][0:5]

    @accepts(None, str)
    @validate_argument_attribute('self')
    def has_children(self, attribute):
        """
        Return if the provided attribute does have children.
        This is the case when we have a fourth entry in the
        list in the value of an entry (the entry corresponding
        to the provided `attribute`-name).
        """
        # copy 5th value of cv definition for better readability of the code
        child_struct = self[attribute][4]
        # check if children should be checked
        if isinstance(child_struct, cv_structure):
            return True
        elif (isinstance(child_struct, bool) and
                child_struct):
            return True
        # return False if we are not definately told to check children
        return False

    @accepts(None, str)
    @validate_argument_attribute('self')
    def get_children(self, attribute):
        """
        Returns value of the child cv_structure if existing; else `None` is
        returned.

        @param attribute str, name of an attribute (key of dict) for which
                                the child should be returned
        @return: optional possible child cv_structure; return value is
                  `True` (all possible child CVs should be tested),
                  `False` (no test of children),
                  `None` (no test of children) or
                  an instance of cv_structure (contains definition on how
                                               and which children to process)
        """
        if (not self.has_children(attribute)):
            return None

        return self[attribute][4]

    @accepts(None, str)
    @validate_argument_attribute('self')
    def has_cv(self, attribute):
        """
        Returns True or False depending on whether this CV structure holds a
            CV for attribute/key `attribute` or needs an external one.

        @param attribute str, name of an attribute (key of dict) for which
                                information on the presence of a CV should be
                                returned
        @return: bool; True if a CV is contained in the CV structure object and
                        False if not (then an external CV has to be provided).
        """
        return (self[attribute][2] is not None)

    @accepts(None, str)
    @validate_argument_attribute('self')
    def get_cv(self, attribute):
        """
        Returns a CV if one is present in this CV structure for attribute/key
            `attribute`. If not present, `None` is returned.

        @param attribute str, name of an attribute (key of dict) for which
                                the CV should be returned
        @return: CV; TODO
        """
        if self.has_cv(attribute):
            return self[attribute][2]
        else:
            return None

    @accepts(None, str)
    def is_operation_allowed(self, operation):
        """
        TODO

        @param operation str, TODO
        @return: bool; True if ...
        """
        return operation in self.__allowed_operations__.keys()

    @accepts(None, str)
    def convert_operation(self, operation):
        """
        TODO

        @param operation str, TODO
        @return: str; officially supported operation
        """
        # get this function's name
        my_name = sys._getframe().f_code.co_name

        # check if the operation is allowed
        if not self.is_operation_allowed(operation):
            raise ValueError('cv_tools.'+my_name+':: provided name of an ' +
                             'operation is not supported: ' + operation)

        return self.__allowed_operations__[operation]

    @accepts(None, str)
    @validate_argument_attribute('self')
    def get_operation(self, attribute):
        """
        TODO

        @param attribute str, TODO
        @return: str; TODO
        """
        # get and convert operation from cv_structure
        return self.convert_operation(self[attribute][0])

    @accepts(None, None)
    def is_cv_prepare_fun_allowed(self, fun):
        """
        TODO

        @param fun str, TODO
        @return: bool; True if ...
        """
        # if fun is `None` or empty str => that's allowed
        if fun is None or (isinstance(fun, str) and len(fun) == 0):
            return True

        # if `fun` is a string then we try to convert it
        if isinstance(fun, str):
            return fun in self.__allowed_cv_preproc_funs__

        return False

    @accepts(None, None)
    def get_cv_prepare_fun_name(self, fun):
        """
        TODO

        @param fun str, TODO
        @return: str or None; officially supported operation
        """

        # no function provided => return empty string
        if fun is None:
            return ''

        # a string provided => return string
        if isinstance(fun, str):
            return fun

        # if `fun` has a `__name__` => return it
        # else => empty string
        try:
            return fun.__name__
        except AttributeError:
            return ''

    @accepts(None, None)
    def convert_cv_prepare_fun(self, fun):
        """
        TODO

        @param fun str, TODO
        @return: str or None; officially supported operation
        """

        # NOTE: If this function is updated, please consider to updating the
        #       variable `self.__allowed_cv_preproc_funs__` as well.

        # get this function's name
        my_name = sys._getframe().f_code.co_name

        # no function provided => return `None`
        if fun is None or (isinstance(fun, str) and len(fun) == 0):
            return None

        # if not a string => TypeError
        if not isinstance(fun, str):
            raise ValueError('cv_tools.' + my_name + ':: provided function h' +
                             'as to be of type `str`; function name (if supp' +
                             'orted): ' + self.get_cv_prepare_fun_name(fun))

        # check if the function is allowed
        if not self.is_cv_prepare_fun_allowed(fun):
            raise ValueError('cv_tools.' + my_name + ':: provided function ' +
                             'to preprocess a CV is not allowed; function ' +
                             'name (if supported): ' +
                             self.get_cv_prepare_fun_name(fun))

        # a string provided => try to get corresponding callable
        if isinstance(fun, str):
            if fun in ['keys', 'dict.keys']:
                return dict.keys
            if fun in ['values', 'dict.values']:
                return dict.values
            raise ValueError('cv_tools.' + my_name + ':: provided name of a ' +
                             'function for preprocessing a CV was not conver' +
                             'ted because not implement. The fact that this ' +
                             'message appears indicates that there is some d' +
                             'iscrepancy between the list of allowed functio' +
                             'n names and the actually processed function na' +
                             'mes. Please inform the developers by posting a' +
                             'n issue at the official GitHub repository of t' +
                             'his plugin. Function name: ' +
                             self.get_cv_prepare_fun_name(fun))

        # we should not arrive here ...
        raise RuntimeError('cv_tools.' + my_name + ':: provided function to ' +
                           'preprocess a CV could not be converted for an ' +
                           'unknown reason; function name (if supported): ' +
                           self.get_cv_prepare_fun_name(fun))

    @accepts(None, str)
    @validate_argument_attribute('self')
    def get_cv_prepare_fun(self, attribute):
        """
        TODO

        @param attribute str, TODO
        @return: callable; TODO
        """
        # Let the other functions to the work
        return self.convert_cv_prepare_fun(self[attribute][3])


def should_process_all_cvs(process_all_cvs):
    """
    TODO

    If an argument of wrong type is passed, we return `False`.
    If an argument of

    @param process_all_cvs bool
    @return True if process_all_cvs equals True,
                    else False
    """
    if(isinstance(process_all_cvs, bool)):
        if process_all_cvs:
            return True

    return False


# Carsten: __allowed_types_for_cvs__, welche muessten da rein?
@accepts(cv_structure, str, __allowed_types_for_cvs__, bool)
@validate_argument_attribute('cv_struct')
def extract_cv(cv_struct, attribute, cvs, guess=False):
    """
    Return a list of values

    TODO: describe behaviour!!!

    """
    # get this function's name
    my_name = sys._getframe().f_code.co_name

    # Get name of the cv ...
    cv_name = cv_struct[attribute][1]

    # check if our CV was provided via cv_struct:
    if cv_struct.has_cv(attribute):
        raw_return_val = cv_struct.get_cv(attribute)

    # if CV was not in cv_struct (cv_struct[attribute][2] is None)
    else:
        # check if the arguments provided via `cvs` is a valid CV dictionary
        try:
            cvs_is_dict = validate_structure_of_cvs(cvs, check_version=False,
                                                    recursive=False)
        except TypeError:
            cvs_is_dict = False

        # if `cvs` is a dict, see if cv named `cv_name` is in it
        if cvs_is_dict:
            # Do some tests with `cv_name`:
            #     Test if `cv_name` is in the CV
            if(cv_name not in cvs.keys()):
                # if no empty key in `cvs` and
                #    `cv_name` is empty
                # then we return the whole `cvs` and
                #      apply (if given) a function

                if(len(cv_name) == 0):
                    raw_return_val = cvs
                else:
                    raise KeyError('cv_tools.'+my_name+':: CV with name ' +
                                   cv_name + ' does not exist in provided ' +
                                   'CV-dictionary')
            else:
                # store return value
                raw_return_val = cvs[cv_name]

        else:
            # if caller does not want that we guess, we throw an error here
            if (not guess):
                raise TypeError('cv_tools.'+my_name+':: arg `cvs` is no vali' +
                                'd CV; please set `guess` to `True` if you w' +
                                'ish me to guess and to try to construct a CV')
            else:
                # ~~~~~ let's guess what we have ~~~~~
                # If cvs is a dict and
                #    we have an non-empty string as cv_name and
                #    cv_name exists in the keys of cvs
                # then we return the values of the dict entry to the
                #    corresponding cv_name as key.
                if(isinstance(cvs, dict)):
                    #     Test if `cv_name` is not in the CV
                    if(cv_name not in cvs.keys()):
                        # then we return the whole `cvs` and
                        #      apply (if given) a function
                        if(len(cv_name) == 0):
                            raw_return_val = cvs
                        else:
                            raise KeyError('cv_tools.'+my_name+':: CV with ' +
                                           'name ' + cv_name + ' does not ' +
                                           'exist in provided CV-dictionary')
                    else:
                        # else return something reasonable
                        raw_return_val = cvs[cv_name]

                # else we return `cvs` and hope the calling func knows how to
                # use `cvs`
                else:
                    # store return value
                    raw_return_val = cvs

    # get function to apply to CV to get a nicer CV for comparison
    cv_fun = cv_struct.get_cv_prepare_fun(attribute)

    # return ...
    if cv_fun is not None:
        # check if the function `cv_fun` can be applied to `raw_return_val`
        try:
            return cv_fun(raw_return_val)
        except TypeError:
            raise TypeError('cv_tools.' + my_name + ':: provided function ' +
                            'with name `' +
                            cv_struct.get_cv_prepare_fun_name(cv_fun) +
                            '` cannot be applied on controlled vocabulary ' +
                            'of type `' + type(raw_return_val).__name__ +
                            '`. If no content was shown between the first ' +
                            'set of quotation marks then no function name ' +
                            'was available.')
    else:
        return raw_return_val


@accepts(cv_structure, str, __allowed_types_for_cvs__, None, bool)
@validate_argument_attribute('cv_struct')
def check_cv(cv_struct, attribute, cvs, value, guess=False):
    """
    TODO

    TODO: check against CVs of operations
    TODO: `return` "not implemented" when allowed operation is not covered

    """
    # get this function's name
    my_name = sys._getframe().f_code.co_name

    # ... extract CV, and ...
    cv = extract_cv(cv_struct, attribute, cvs, guess)
    # ... get operation.
    operation = cv_struct.get_operation(attribute)

    # ~~~~~ perform some checks and preparation ~~~~~
    # for IN, NOT IN, CONTAINS ANY and CONTAINS ALL
    if (operation in ['in', 'not_in', 'contains_any', 'contains_all']):
        # ~~~~~ if our cv is `iterable` and not a `str`, we keep it as is ~~~~~
        # test for iterable
        try:
            cv.__iter__
            # If we reach here, we are iterable. Therefore, we test for string.
            # We could do this outside of the try-except block. However, by
            # doing it this way we simplify the modification of this code.
            if (isinstance(cv, str)):
                raise AttributeError('dummy error to enter `except` clause')
        except AttributeError:
            # if we get an AttributeError it is non-`iterable` or a string
            # we put it into a list
            cv = [cv]

        # get first type of value
        value_type = type(value)
        # check if `value` and content of `cv` are of same type
        if(any(not isinstance(c, value_type) for c in cv)):
            raise TypeError('cv_tools.'+my_name+':: value to check and ' +
                            'values in the CV are of different types')

    # for ISINSTANCE
    if (operation == 'isinstance'):
        if (not isinstance_recursive_tuple(cv, type)):
            raise TypeError('cv_tools.'+my_name+':: When operation `isinstan' +
                            'ce` is chosen, the provided CV or individual va' +
                            'riable has to be of type `type` or a tuple cont' +
                            'aining `type`s.')

    # for REGEX
    if (operation == 'regex'):
        if (isinstance(cv, list)):
            if (len(cv) == 1):
                cv = cv[0]
            else:
                raise ValueError('cv_tools.'+my_name+':: When operation ' +
                                 '`regex` is chosen and the provided CV is ' +
                                 'of type list, then the list has to be of ' +
                                 'length 1 (one) and has to contain a `str`')
        if (not isinstance(value, str)):
            raise TypeError('cv_tools.'+my_name+':: When operation `regex` ' +
                            'is chosen, the provided value to check has to ' +
                            'be one item of type `str`.')
        if (not isinstance(cv, str)):
            raise TypeError('cv_tools.'+my_name+':: When operation `regex` ' +
                            'is chosen, the provided CV has to be one item ' +
                            'of type `str`.')
        # convert CMIP6 license text into a regex
        # NOTE: The CMIP6 CV contains a pseudo-regex of the license text.
        #       We need to convert it into a proper python-regex, first.
        #  replace tags like `<TEXT>`
        str_regex_tag01 = '<[^<>]*>'
        regex_tag01 = re.compile(str_regex_tag01)
        #  replace tags like `[TEXT]`
        str_regex_tag02 = '[-]?\[[^[\]]*\]'
        regex_tag02 = re.compile(str_regex_tag02)
        #  replace URLs starting with `https://` or `http://`
        str_regex_url = 'http[s]:\/\/[^\s\)]*'
        regex_url = re.compile(str_regex_url)
        # replace words with underscore
        str_regex_underscore = '[a-zA-Z0-9]+(_[a-zA-Z0-9]+)+'
        regex_underscore = re.compile(str_regex_underscore)
        # replace parenthese
        str_regex_parentheses_open = '\('
        str_regex_parentheses_close = '\)'
        regex_parentheses_open = re.compile(str_regex_parentheses_open)
        regex_parentheses_close = re.compile(str_regex_parentheses_close)
        #  prepare real regex
        str_regex_cv = '^'+re.sub(regex_parentheses_open, '\(',
                                  re.sub(regex_parentheses_close, '\)',
                                         re.sub(regex_underscore, '.*',
                                                re.sub(regex_tag01, '.*',
                                                       re.sub(regex_tag02,
                                                              '.*',
                                                              re.sub(regex_url,
                                                                     '.*', cv)
                                                              )))))+'$'
        regex_cv = re.compile(str_regex_cv)
        # match regex
        if re.fullmatch(regex_cv, value):
            return True
        else:
            return False

    # ['in', 'not_in', 'regex', 'isinstance', 'contains_any', 'contains_all']
    # IN
    if (operation == 'in'):
        if (value in cv):
            return True
        else:
            return False

    # NOT IN
    if (operation == 'not_in'):
        if (value not in cv):
            return True
        else:
            return False

    # IS INSTANCE
    if (operation in 'isinstance'):
        if (isinstance(value, cv)):
            return True
        else:
            return False

    # CONTAINS ANY
    if (operation == 'contains_any'):
        if (any([c in value for c in cv])):
            return True
        else:
            return False

    # CONTAINS ALL
    if (operation == 'contains_all'):
        if (not any([c not in value for c in cv])):
            return True
        else:
            return False

    # When we reach here something went wrong.
    raise ValueError('cv_tools.'+my_name+':: Operation `' + operation + '` d' +
                     'oes not seem to be supported. Otherwise, you would not' +
                     ' get this error. However, not-implemented operations s' +
                     'hould have been captured far earlier. Therefore, pleas' +
                     'e inform the developers by posting an issue at the off' +
                     'icial GitHub repository of this plugin.')


@accepts(dict, bool, bool)
def validate_structure_of_cvs(cvs, check_version=False, recursive=True):
    """
    TODO

    TODO: find examples for "bad" CVs; when a CV should be bad? see issue #3
    TODO: think about this in more general

    """

    # get function's name
    # NOTE: keep this; we might need it later on
    my_name = sys._getframe().f_code.co_name

    # iterate the keys and values of the CV

    if(isinstance(cvs, dict)):
        if(recursive):
            for k, v in cvs.items():
                if(isinstance(v, dict)):
                    # We pass `False` for `check_version` because information
                    # on the version is only available on the top level.
                    if(not validate_structure_of_cvs(v, check_version=False,
                                                     recursive=False)):
                        return False
    else:
        return False

    # check for the key `version_metadata` and its content
    if(check_version):
        # key not in cvs => return False
        if(__name__version_metadata__ not in cvs.keys()):
            return False
        # get metadata entry
        metadata = cvs[__name__version_metadata__]
        # entry/value to `version_metadata` in cvs is not a dict => False
        if(not isinstance(metadata, dict)):
            return False
        # necessary metadata information (as keys) not in selected entry/value
        if(any([k not in metadata.keys()
                for k in __content__version_metadata__.keys()])):
            return False
        # check of entries with metadata information have bad types
        for k, v in __content__version_metadata__.items():
            if(not isinstance(metadata[k], v)):
                return False

    # Everything is fine if we did not `return` yet.
    return True
