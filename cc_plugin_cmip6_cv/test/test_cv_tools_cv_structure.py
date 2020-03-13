from cc_plugin_cmip6_cv.cv_tools import cv_structure
import cc_plugin_cmip6_cv.cv_tools as cv_tools
import pytest
import numpy
import inspect


### ~~~~~~~~~~~~~~~~~~~~~~ DEFINE TEST DATA ~~~~~~~~~~~~~~~~~~~~~~
##  replicate internal data structures of `cv_structure`
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
__allowed_cv_preproc_funs__ = ['keys', 'dict.keys', 'values',
                               'dict.values']
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
__cmip6_cv_ignore__ = ["activity_participation",
                       "additional_allowed_model_components", "cohort",
                       "description", "end_year", "label_extended", "label",
                       "min_number_yrs_per_sim", "model_component",
                       "release_year", "required_model_components",
                       "start_year", "tier"]

## create a CV
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
#   check allowed operations; no error
dummy_cv_struct_good_02 = {'attr01': ['in', 'cv01', None, 'keys', False],
                           'attr02': ['in', 'cv01', None, 'values', False],
                           'attr03': ['in', 'cv02', None, '', False],
                           'attr04': ['not in', 'cv01', None, 'keys', False],
                           'attr05': ['regex', 'cv03', None, '', False],
                           'attr06': ['isinstance', 'blub', numpy.int32, '',
                                      False],
                           'attr07': ['contains any', 'cv04', None, '', False],
                           'attr08': ['contains all', 'cv05', None, '', False]}
#   check sub-cv_structure; no error
dummy_cv_struct_good_03 = {'attr01': ['in', 'cv01', None, 'keys', False],
                           'attr02': ['in', 'cv01', None, 'values', False],
                           'attr09': ['in', 'cv06', None, 'keys',
                                      cv_structure({'attr03': dummy_cv_struct_good_02['attr03']})],
                           'attr10': ['in', 'cv07', None, 'keys', True],
                           'attr11': ['in', '', None, '', False],
                           'attr12': ['in', 'cv99', None, '', False],
                           'attr13': ['in', '', None, 'keys', False]}
#   wrong value; ValueError
dummy_cv_struct_bad_01 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': ['BAD VALUE', 'cv01', None, 'values', False]}
#   wrong type in list in value; TypeError
dummy_cv_struct_bad_02 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': [5, 'cv01', None, 'values', False]}
#   too short list; ValueError
dummy_cv_struct_bad_03 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': ['in', 'cv01', None, False]}
#   too long list; ValueError
dummy_cv_struct_bad_04 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': ['in', 'cv01', None, 'values', False, 'a str']}
#   wrong type of value; TypeError
dummy_cv_struct_bad_05 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': 5}
#   wrong type of fourth value in list in value; TypeError
dummy_cv_struct_bad_06 = {'attr01': ['in', 'cv01', None, 'keys', False],
                          'attr02': ['in', 'cv01', None, 'values', 'a string']}
#   this structure is correct but it contains wrong names of CVs
#   TODO: this bad cv_struct is not used
dummy_cv_struct_bad_07 = {'attr11': ['in', 'cv99', None, 'keys', False],
                          'attr12': ['in', 'cv99', None, 'values', False]}

# put the tests into lists to iterate them more simply
list_cv_structs_NoError = [dummy_cv_struct_good_01,
                           dummy_cv_struct_good_02,
                           dummy_cv_struct_good_03]
list_cv_structs_ValueError = [dummy_cv_struct_bad_01,
                              dummy_cv_struct_bad_03,
                              dummy_cv_struct_bad_04]
list_cv_structs_TypeError = [dummy_cv_struct_bad_02,
                             dummy_cv_struct_bad_05,
                             dummy_cv_struct_bad_06]


def test_cv_tools_constants():

    # set global module-variables to check
    test_constants = ['__name__version_metadata__',
                      '__content__version_metadata__',
                      '__allowed_types_for_cvs__', '__cmip6_cv_ignore__']
    # get global module-variables of module cv_tools
    cv_tools_members = dict(inspect.getmembers(cv_tools))

    # iterate global variables and compare them
    for const in test_constants:
        assert globals()[const] == cv_tools_members[const]


def test_cv_structure_constants():

    # set global module-variables to check
    test_constants = ['__allowed_operations__', '__allowed_cv_preproc_funs__']
    # get global module-variables of module cv_tools
    cv_tools_members = dict(inspect.getmembers(cv_tools.cv_structure))

    # iterate global variables and compare them
    for const in test_constants:
        assert globals()[const] == cv_tools_members[const]


def test_cv_structure():
    ### ~~~~~~~~~~~~~~~~~~~~~~ TEST __init__ ~~~~~~~~~~~~~~~~~~~~~~
    ##  test `__init__` call itself
    # call `__init__` successful and get back an instance of `cv_struture`
    for test_dict in list_cv_structs_NoError:
        assert isinstance(cv_structure(test_dict), cv_structure)
    # throw and catch `ValueError`
    for test_dict in list_cv_structs_ValueError:
        with pytest.raises(ValueError):
            dummy_cv_structure = cv_structure(test_dict)
    # throw and catch `TypeError`
    for test_dict in list_cv_structs_TypeError:
        with pytest.raises(TypeError):
            dummy_cv_structure = cv_structure(test_dict)
    
    ## test whether data is properly saved by __init__
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_01)
    # test keys
    assert dummy_cv_struct_good_01.keys() == dummy_cv_structure.keys()
    # test values
    assert not any([values not in dummy_cv_structure.values() for values in dummy_cv_struct_good_01.values()])
    assert not any([values not in dummy_cv_struct_good_01.values() for values in dummy_cv_structure.values()])

    ### ~~~~~~~~~~~~~~~~~~~~~~ TEST FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~
    ##    get_attributes_to_check
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_01)
    assert dummy_cv_struct_good_01.keys() == dummy_cv_structure.get_attributes_to_check()

    ##    get_cv_names_needed
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_01)
    cvs_A = set([values[1] for values in dummy_cv_struct_good_01.values() if isinstance(values[1], str)])
    cvs_B = set(dummy_cv_structure.get_cv_names_needed())
    assert 0 == len(cvs_A.symmetric_difference(cvs_B))

    ##    get_cv_check_definition
    #       initialize cf_structure
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_01)
    keys = list(dummy_cv_structure)
    #       do non-error tests
    #           test 01, equal output
    input_good = keys[0]
    output_good = dummy_cv_struct_good_01[input_good]
    assert output_good == dummy_cv_structure.get_cv_check_definition(input_good)
    #           test 02, inequal output
    input_good = keys[0]
    output_bad = dummy_cv_struct_good_01[keys[1]]
    assert output_bad != dummy_cv_structure.get_cv_check_definition(input_good)
    #       throw errors
    #           test 03, bad type
    input_bad = 1
    with pytest.raises(TypeError):
        dummy_cv_structure.get_cv_check_definition(input_bad)
    #           test 04, bad value
    input_bad = 'bad_attribute_value'
    with pytest.raises(ValueError):
        dummy_cv_structure.get_cv_check_definition(input_bad)

    ##    has_children
    #       initialize cf_structure
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_03)
    keys = list(dummy_cv_structure)
    #       do non-error tests
    #           test 01, output: True
    output_true = True
    input_true = keys[2]
    assert output_true == dummy_cv_structure.has_children(input_true)
    #           test 02, output: False
    output_false = False
    input_false = keys[0]
    assert output_false == dummy_cv_structure.has_children(input_false)
    #       throw errors
    #           test 03, bad type
    input_bad = 1
    with pytest.raises(TypeError):
        dummy_cv_structure.has_children(input_bad)
    #           test 04, bad value
    input_bad = 'bad_attribute_value'
    with pytest.raises(ValueError):
        dummy_cv_structure.has_children(input_bad)

    ##    get_children
    #       initialize cf_structure
    dummy_cv_structure = cv_structure(dummy_cv_struct_good_03)
    keys = list(dummy_cv_structure)
    #       do non-error tests
    #           test 01, output: some reasonable output
    input_exist = keys[2]
    output_exist = dummy_cv_struct_good_03[input_exist][4]
    assert output_exist == dummy_cv_structure.get_children(input_exist)
    #           test 02, output: not None
    output_none = None
    assert output_none is not dummy_cv_structure.get_children(input_exist)
    #           test 03, output: True
    input_exist = keys[3]
    output_exist = True
    assert output_exist == dummy_cv_structure.get_children(input_exist)
    #           test 04, output: None
    input_notexists = keys[0]
    output_none = None
    assert output_none is dummy_cv_structure.get_children(input_notexists)
    #       throw errors
    #           test 05, bad type
    input_bad = 1
    with pytest.raises(TypeError):
        dummy_cv_structure.get_children(input_bad)
    #           test 06, bad value
    input_bad = 'bad_attribute_value'
    with pytest.raises(ValueError):
        dummy_cv_structure.get_children(input_bad)

    # todo: test operations CV from cv_struture


@pytest.mark.skip(reason="test function not implemented yet")
def test_has_cv():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_get_cv():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_is_operation_allowed():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_convert_operation():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_get_operation():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_is_cv_prepare_fun_allowed():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_get_cv_prepare_fun_name():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_convert_cv_prepare_fun():
    pass


@pytest.mark.skip(reason="test function not implemented yet")
def test_get_cv_prepare_fun():
    pass
