from cc_plugin_cmip6_cv.cv_tools import cv_structure, \
        validate_argument_attribute
import pytest


# ~~~~~~~~~~~~~~~~~~~~~~ DEFINE TEST DATA ~~~~~~~~~~~~~~~~~~~~~~
process_all_available_cvs = True

# create a CV
dummy_cv = {'cv01': {'DKRZ': 'Deutsches Klimarechenzentrum',
                        'mfg': 'Mit freundlichen Gruessen',
                        'asap': 'as soon as possible'},
            'cv02': ['red', 'green', 'blue', 'pink', 'gray', 'grey'],
            'cv03': ['A[0-9]B[0-9]{2,}C'],
            'cv04': ['apple', 'peach', 'cherry'],
            'cv05': ['CF', 'UGrid'],
            'cv06': {'car': {'cv02': ['red', 'green']},
                     'bike': {'cv02': ['red', 'blue', 'pink']},
                     'boat': {'cv02': ['green', 'blue']}},
            'cv07': {'laptop': {'cv02': ['red', 'green', 'gray', 'grey']},
                     'desktop': {'cv02': ['red', 'pink', 'green', 'gray']},
                     'tablet': {'cv02': ['blue', 'gray', 'grey', 'red']}},
            'version_metadata': {'CV_collection_modified': 'Thu Jan  2 11:58' +
                                                           ':27 2020 -0800',
                                 'CV_collection_version': '6.2.45.3',
                                 'author': 'Paul J. Durack <durack1@llnl.gov>',
                                 'institution_id': 'PCMDI',
                                 'institution_id_CV_modified': 'Thu Nov 14 1' +
                                                               '1:18:04 2019' +
                                                               ' -0800',
                                 'institution_id_CV_note': 'Register institu' +
                                                           'tion_id UCI',
                                 'previous_commit': '59b6eaaa02885cc21de330a' +
                                                    '393944c43e19c899b',
                                 'specs_doc': 'v6.2.7 (10th September 2018; ' +
                                              'https://goo.gl/v1drZl)'}}

## create dictionaries to test the `__init__` and as base for other tests
#   some basic structure; no error
dummy_cv_struct_good_01 = {'attr01': ['in', 'cv01', None, 'keys', False],
                           'attr02': ['in', 'cv01', None, 'values', False]}


def test__cv_tools__validate_argument_attribute():
    # see: https://stackoverflow.com/questions/34648337/how-to-test-a-decorator-in-a-python-package/34648674

    # input data:
    #   some basic cv_structure
    dummy_cv_struct = cv_structure(dummy_cv_struct_good_01)

    # some successful tests
    #   try correct attribute
    #   name of instance of cv_structure: `cv_struct`
    #   => no error
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attribute):
        return cv_struct[attribute]
    assert dummy_cv_struct['attr01'] == dummy_fun(dummy_cv_struct, 'attr01')

    #   try another correct attribute
    #   name of instance of cv_structure: `cv_struct`
    #   => no error
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attribute):
        return cv_struct[attribute]
    assert dummy_cv_struct['attr02'] == dummy_fun(dummy_cv_struct, 'attr02')

    #   try correct attribute
    #   name of instance of cv_structure: `self`
    #   => no error
    @validate_argument_attribute(None)
    def dummy_fun(self, attribute):
        return self[attribute]
    assert dummy_cv_struct['attr01'] == dummy_fun(dummy_cv_struct, 'attr01')

    #   try correct attribute
    #   name of instance of cv_structure: `self`, mention `self` in decorator
    #   => no error
    @validate_argument_attribute('self')
    def dummy_fun(self, attribute):
        return self[attribute]
    assert dummy_cv_struct['attr01'] == dummy_fun(dummy_cv_struct, 'attr01')

    #   try correct attribute
    #   name of instance of cv_structure: `abc`; mention `abc` in decorator
    #   => no error
    @validate_argument_attribute('abc')
    def dummy_fun(abc, attribute):
        return abc[attribute]
    assert dummy_cv_struct['attr01'] == dummy_fun(dummy_cv_struct, 'attr01')

    # test with errors
    #   try correct attribute
    #   name of instance of cv_structure: `blub`
    #   => RuntimeError
    @validate_argument_attribute(None)
    def dummy_fun(blub, attribute):
        return blub[attribute]
    with pytest.raises(RuntimeError):
        dummy_fun(dummy_cv_struct, 'attr01')

    #   try correct attribute
    #   provide instance of `str` as argument `cv_struct`
    #   => RuntimeError
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attribute):
        return cv_struct[attribute]
    with pytest.raises(RuntimeError):
        dummy_fun('a bad value', 'attr01')

    #   try incorrect attribute
    #   name of instance of cv_structure: `cv_struct`
    #   => ValueError
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attribute):
        return cv_struct[attribute]
    with pytest.raises(ValueError):
        dummy_fun(dummy_cv_struct, 'attr03')

    #   try wrong type for attribute
    #   name of instance of cv_structure: `cv_struct`
    #   => TypeError
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attribute):
        return cv_struct[attribute]
    with pytest.raises(TypeError):
        dummy_fun(dummy_cv_struct, 77)

    #   do not have the attribute
    #   name of instance of cv_structure: `cv_struct`
    #   => RuntimeError
    @validate_argument_attribute(None)
    def dummy_fun(cv_struct, attr):
        return cv_struct[attr]
    with pytest.raises(RuntimeError):
        dummy_fun(dummy_cv_struct, 'attr01')
