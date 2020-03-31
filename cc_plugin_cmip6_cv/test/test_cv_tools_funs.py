from cc_plugin_cmip6_cv.cv_tools import cv_structure, extract_cv, check_cv, \
        validate_structure_of_cvs, should_process_all_cvs
import pytest
import numpy


### ~~~~~~~~~~~~~~~~~~~~~~ DEFINE TEST DATA ~~~~~~~~~~~~~~~~~~~~~~
##  replicate internal data structures of `cv_structure`
allowed_operations = ['in', 'not in', 'regex', 'isinstance', 'contains any',
                      'contains all']
# allowed_cv_preproc_funs = ['keys', 'values']
name__version_metadata = 'version_metadata'
content__version_metadata = {"CV_collection_modified": str,
                             "CV_collection_version": str,
                             "author": str,
                             "institution_id": str,
                             "institution_id_CV_modified": str,
                             "institution_id_CV_note": str,
                             "previous_commit": str,
                             "specs_doc": str}

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
                           'attr13': ['in', '', None, 'keys', False],
                           'attr14': None}
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

dummy_cv_struct_good_01 = cv_structure(dummy_cv_struct_good_01)
# TODO: proceed here!


def test__cf_tools__should_process_all_cvs():

    # successful: True
    assert should_process_all_cvs(True)

    # not successful: False
    assert not should_process_all_cvs(5)
    assert not should_process_all_cvs('test string')
    assert not should_process_all_cvs(False)
    assert not should_process_all_cvs(None)
    assert not should_process_all_cvs(4.3)
    assert not should_process_all_cvs([4, 3])


# @pytest.mark.skip(reason="tested function not implemented yet")
def test__cv_tools__extract_cv():
    # TODO: extend test to check the output-cv when `list`[2] is not None

    # input data:
    #   some basic cv_structure
    dummy_cv_struct_good = cv_structure(dummy_cv_struct_good_03)
    dummy_cv_struct_bad_cv_name = cv_structure(dummy_cv_struct_bad_07)

    ## some successful tests
    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   correct cv
    #   => no error
    assert dummy_cv[dummy_cv_struct_good['attr01'][1]].keys() == extract_cv(dummy_cv_struct_good, 'attr01', dummy_cv)
    # the `keys` is in `dummy_cv_struct_good['attr01'][2]`

    #   name of instance of cv_structure: `cv_struct`
    #   try another correct attribute
    #   correct cv
    #   => no error
    output_expected = set(dummy_cv[dummy_cv_struct_good['attr02'][1]].values())
    output_present = set(extract_cv(dummy_cv_struct_good, 'attr02', dummy_cv))
    # the `values` is in `dummy_cv_struct_good['attr02'][2]`
    assert 0 == len(output_present.symmetric_difference(output_expected))

    #   name of instance of cv_structure: `cv_struct`
    #   try another correct attribute; the corresponding CV consists of sub-CVs
    #   correct cv
    #   => no error
    assert dummy_cv[dummy_cv_struct_good['attr09'][1]].keys() == extract_cv(dummy_cv_struct_good, 'attr09', dummy_cv)
    # the `keys` is in `dummy_cv_struct_good['attr09'][2]`

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   correct cv
    #   guess = False
    #   => no error
    assert dummy_cv[dummy_cv_struct_good['attr01'][1]].keys() == extract_cv(dummy_cv_struct_good, 'attr01', dummy_cv, False)
    # the `keys` is in `dummy_cv_struct_good['attr01'][2]`

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   correct cv
    #   guess = True
    #   => no error
    assert dummy_cv[dummy_cv_struct_good['attr01'][1]].keys() == extract_cv(dummy_cv_struct_good, 'attr01', dummy_cv, True)
    # the `keys` is in `dummy_cv_struct_good['attr01'][2]`

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   list as cv
    #   guess = True
    #   => no error
    example_list = ['abc', 'def']
    assert example_list == extract_cv(dummy_cv_struct_good, 'attr11', example_list, True)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   => no error
    example_dict = {'cv99': ['abc', 'def']}
    # 'cv99' equals dummy_cv_struct_good['attr12'][1]
    assert example_dict['cv99'] == extract_cv(dummy_cv_struct_good, 'attr12', example_dict, True)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   => no error
    example_dict = {'': ['abc', 'def']}
    # '' equals dummy_cv_struct_good['attr11'][1]
    assert example_dict[''] == extract_cv(dummy_cv_struct_good, 'attr11', example_dict, True)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   => no error
    example_dict = {'cv99': ['abc', 'def']}
    # '' equals dummy_cv_struct_good['attr11'][1]; if '' is not a key in the
    # cv (as it is in this case; `example_dict` is the cv) then we get back the
    # original dict/cv/example_dict (except it an additional function was 
    #  applied; which was not the case here);
    output_expected = example_dict
    output_present = extract_cv(dummy_cv_struct_good, 'attr11', example_dict, True)
    assert output_expected.keys() == output_present.keys()
    assert 0 == len(set(output_present).symmetric_difference(set(output_expected)))

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   => no error
    example_dict = {'cv99': ['abc', 'def']}
    # 'cv99' is just a dummy key
    # dummy_cv_struct_good['attr13'][1] is empty string but
    # dummy_cv_struct_good['attr13'][2] contains `keys` (function to apply)
    assert example_dict.keys() == extract_cv(dummy_cv_struct_good, 'attr13', example_dict, True)

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   guess = True
    #   => no error
    assert 42 == extract_cv(dummy_cv_struct_good, 'attr11', 42, True)

    ## tests with erros
    #   provide instance of `str` as argument `cv_struct`
    #   try correct attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = extract_cv('a bad value', 'attr01', dummy_cv)

    #   name of instance of cv_structure: `cv_struct`
    #   try incorrect attribute
    #   correct cv
    #   => ValueError
    with pytest.raises(ValueError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr03', dummy_cv)

    #   name of instance of cv_structure: `cv_struct`
    #   try wrong type for attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = extract_cv(dummy_cv_struct_good, 77, dummy_cv)

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr01', 42)

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   guess = False (default)
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr01', 42, False)

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute; but the corresponding CV is not in dummy_cv
    #   correct cv but it does not requested cv
    #   => KeyError
    with pytest.raises(KeyError):
        tmp = extract_cv(dummy_cv_struct_bad_cv_name, 'attr11', dummy_cv)
    
    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   correct cv
    #   wrong type of guess
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr01', dummy_cv, 5)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   list as cv
    #   guess = True
    #   but dummy_cv_struct_good['attr13'][2] contains a function that cannot
    #       be applied to `example_list`
    #   => TypeError
    example_list = ['abc', 'def']
    with pytest.raises(TypeError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr13', example_list, True)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   dummy_cv_struct_good['attr12'][1] not in example_dict
    example_dict = {'cv98': ['abc', 'def']}
    # 'cv99' is dummy_cv_struct_good['attr12'][1] but is not in `example_dict`
    with pytest.raises(KeyError):
        tmp = extract_cv(dummy_cv_struct_good, 'attr12', example_dict, True)


dummy_cv_struct_good_A = cv_structure(dummy_cv_struct_good_01)
dummy_cv_struct_good_B = cv_structure(dummy_cv_struct_good_03)
dummy_cv_struct_bad_cv_name = cv_structure(dummy_cv_struct_bad_07)

@pytest.mark.parametrize(
    "args,output",
    [([dummy_cv_struct_good_B, 'attr01', dummy_cv, 'DKRZ'], True),
     ([dummy_cv_struct_good_B, 'attr01', dummy_cv, 'ARD'], False),
     ([dummy_cv_struct_good_B, 'attr02', dummy_cv, 'Deutsches Klimarechenzentrum'], True),
     ([dummy_cv_struct_good_B, 'attr02', dummy_cv, 'A wrong string'], False),
     ([dummy_cv_struct_good_B, 'attr09', dummy_cv, 'car'], True),
     ([dummy_cv_struct_good_B, 'attr09', dummy_cv, 'ship'], False)]
)
def test_check_cv_auto(args, output):
    assert output == check_cv(*args)


# @pytest.mark.skip(reason="tested function not implemented yet")
def test__cv_tools__check_cv():
    """

    """
    ## prepare input data
    dummy_cv_struct_good_A = cv_structure(dummy_cv_struct_good_01)
    dummy_cv_struct_good_B = cv_structure(dummy_cv_struct_good_03)
    dummy_cv_struct_bad_cv_name = cv_structure(dummy_cv_struct_bad_07)


    # TODO: test:
    # ##  check_cv(cv_struct, attribute, cvs, value)
    # check_cv(dummy_cv_struct_good_A, 'attr01', dummy_cv, 5)
    # TODO: define tests here!

    # TODO: check if value and cv are of different types

    ## take modified versions of non-error tests of `extract_cv` here


    ## tests with erros
    #   provide instance of `str` as argument `cv_struct`
    #   try correct attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv('a bad value', 'attr01', dummy_cv, 'DKRZ')

    #   name of instance of cv_structure: `cv_struct`
    #   try incorrect attribute
    #   correct cv
    #   => ValueError
    with pytest.raises(ValueError):
        tmp = check_cv(dummy_cv_struct_good_A, 'attr03', dummy_cv, 'DKRZ')

    #   name of instance of cv_structure: `cv_struct`
    #   try wrong type for attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_A, 77, dummy_cv, 'DKRZ')

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_A, 'attr01', 42, 'DKRZ')

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute; but the corresponding CV is not in dummy_cv
    #   correct cv but it does not requested cv
    #   => KeyError
    with pytest.raises(KeyError):
        tmp = check_cv(dummy_cv_struct_bad_cv_name, 'attr11', dummy_cv, 'DKRZ')

    ## repeat error-test from `extract_cv`
    #   provide instance of `str` as argument `cv_struct`
    #   try correct attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv('a bad value', 'attr01', dummy_cv, 'a string to check')

    #   name of instance of cv_structure: `cv_struct`
    #   try incorrect attribute
    #   correct cv
    #   => ValueError
    with pytest.raises(ValueError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr03', dummy_cv, 'a string to check')

    #   name of instance of cv_structure: `cv_struct`
    #   try wrong type for attribute
    #   correct cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_B, 77, dummy_cv, 'a string to check')

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr01', 42, 'a string to check')

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute
    #   wrong type of cv
    #   guess = False (default)
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr01', 42, 'a string to check', False)

    #   name of instance of cv_structure: `cv_struct`
    #   correct attribute; but the corresponding CV is not in dummy_cv
    #   correct cv but it does not requested cv
    #   => KeyError
    with pytest.raises(KeyError):
        tmp = check_cv(dummy_cv_struct_bad_cv_name, 'attr11', dummy_cv, 'a string to check')
    
    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   correct cv
    #   wrong type of guess
    #   => TypeError
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr01', dummy_cv, 'a string to check', 5)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   list as cv
    #   guess = True
    #   but dummy_cv_struct_good['attr13'][2] contains a function that cannot
    #       be applied to `example_list`
    #   => TypeError
    example_list = ['abc', 'def']
    with pytest.raises(TypeError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr13', example_list, 'a string to check', True)

    #   name of instance of cv_structure: `cv_struct`
    #   try correct attribute
    #   dict as cv
    #   guess = True
    #   dummy_cv_struct_good['attr12'][1] not in example_dict
    example_dict = {'cv98': ['abc', 'def']}
    # 'cv99' is dummy_cv_struct_good['attr12'][1] but is not in `example_dict`
    with pytest.raises(KeyError):
        tmp = check_cv(dummy_cv_struct_good_B, 'attr12', example_dict, 'a string to check', True)


# @pytest.mark.skip(reason="tested function not implemented yet")
def test__cv_tools__validate_structure_of_cvs():
    # test input
    another_cv = {'cv01': dummy_cv['cv01'],
                  'cv02': dummy_cv['cv02'],
                  'cv03': dummy_cv['cv03'],
                  'cv04': dummy_cv['cv04'],
                  'cv05': dummy_cv['cv05'],
                  'cv06': dummy_cv['cv06'],
                  'cv07': dummy_cv['cv07']}
    cv_bad_metaA = {'cv01': dummy_cv['cv01'],
                    'cv02': dummy_cv['cv02'],
                    'cv03': dummy_cv['cv03'],
                    'cv04': dummy_cv['cv04'],
                    'cv05': dummy_cv['cv05'],
                    'cv06': dummy_cv['cv06'],
                    'cv07': dummy_cv['cv07'],
                    name__version_metadata: 'wrong type'}
    key_for_modification = list(content__version_metadata.keys())[0]
    cv_bad_metaB = {'cv01': dummy_cv['cv01'],
                    'cv02': dummy_cv['cv02'],
                    'cv03': dummy_cv['cv03'],
                    'cv04': dummy_cv['cv04'],
                    'cv05': dummy_cv['cv05'],
                    'cv06': dummy_cv['cv06'],
                    'cv07': dummy_cv['cv07'],
                    name__version_metadata: content__version_metadata.copy()}
    cv_bad_metaB[name__version_metadata].pop(key_for_modification)
    cv_bad_metaC = {'cv01': dummy_cv['cv01'],
                    'cv02': dummy_cv['cv02'],
                    'cv03': dummy_cv['cv03'],
                    'cv04': dummy_cv['cv04'],
                    'cv05': dummy_cv['cv05'],
                    'cv06': dummy_cv['cv06'],
                    'cv07': dummy_cv['cv07'],
                    name__version_metadata: content__version_metadata.copy()}
    cv_bad_metaC[name__version_metadata][key_for_modification] = 4

    ## validate_structure_of_cvs(cvs)
    #   cvs with a key of value `__name__version_metadata__`
    assert validate_structure_of_cvs(dummy_cv)
    #   cvs without a key of value `__name__version_metadata__`
    assert validate_structure_of_cvs(another_cv)
    #   cvs with a key of value `__name__version_metadata__`
    #   with `check_version = True`
    assert validate_structure_of_cvs(dummy_cv, check_version=True)
    #   cvs with a key of value `__name__version_metadata__`
    #   with `check_version = False`
    assert validate_structure_of_cvs(dummy_cv, check_version=False)
    #   cvs without a key of value `__name__version_metadata__`
    #   with `check_version = True`
    assert not validate_structure_of_cvs(another_cv, check_version=True)
    #   cvs without a key of value `__name__version_metadata__`
    #   with `check_version = False`
    assert validate_structure_of_cvs(another_cv, check_version=False)
    #   cvs with a key of value `__name__version_metadata__`
    #   with `recursive = False`
    assert validate_structure_of_cvs(dummy_cv, recursive=False)
    #   cvs with a key of value `__name__version_metadata__`
    #   with `recursive = True`
    assert validate_structure_of_cvs(dummy_cv, recursive=True)
    #   cvs with a key of value `__name__version_metadata__`
    #       but entry/value has wrong type
    #   with `check_version = True`
    assert not validate_structure_of_cvs(cv_bad_metaA, check_version=True)
    #   cvs with a key of value `__name__version_metadata__`
    #       but in the dict of entry/value there is one key missing
    #   with `check_version = True`
    assert not validate_structure_of_cvs(cv_bad_metaB, check_version=True)
    #   cvs with a key of value `__name__version_metadata__`
    #       but in the dict of entry/value there an entry/value a wrong value
    #   with `check_version = True`
    assert not validate_structure_of_cvs(cv_bad_metaC, check_version=True)

    ## throw some errors
    #   provide wrong type for dummy_cv
    #   provide correct type for `check_version`
    with pytest.raises(TypeError):
        validate_structure_of_cvs(42, check_version=True)
    #   provide correct type for dummy_cv
    #   provide wrong type for `check_version`
    with pytest.raises(TypeError):
        validate_structure_of_cvs(dummy_cv, check_version=5)
    #   provide wrong type for dummy_cv
    #   provide wrong type for `check_version`
    with pytest.raises(TypeError):
        validate_structure_of_cvs(42, check_version=5)
    #   provide correct type for dummy_cv
    #   provide correct type for `check_version`
    #   provide wrong type for `recursive`
    with pytest.raises(TypeError):
        validate_structure_of_cvs(dummy_cv, check_version=True, recursive=4)

    # todo: test operations CV from cv_struture
