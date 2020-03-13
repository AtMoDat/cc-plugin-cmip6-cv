#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
cc_plugin_cmip6_cv.cmip6_cv.py

Compliance Test Suite for checking global attributes against controlled
vocabularies of CMIP6.

Web Links
* https://github.com/neumannd/cc-plugin-cmip6cv
* https://github.com/ioos/compliance-checker
* https://github.com/WCRP-CMIP/CMIP6_CVs
'''

from __future__ import (absolute_import, division, print_function)
from compliance_checker import __version__
from compliance_checker.base import BaseNCCheck, BaseCheck, Result
from cc_plugin_cmip6_cv.cv_tools import cv_structure, check_cv, \
                                       should_process_all_cvs
from cc_plugin_cmip6_cv.util import read_cmip6_json_cv, update_cmip6_json_cv, \
                                   data_directory_collection, accepts

import sys
import netCDF4 as nc
import cc_plugin_cmip6_cv.cv_tools as cv_tools


class CMIP6CVBaseCheck(BaseCheck):
    _cc_spec_version = '0.0'
    _cc_spec = 'cmip6_cv'
    _cc_checker_version = __version__
    _cc_url = 'https://github.com/neumannd/cc-plugin-cmip6-cv'
    _cc_display_headers = {
        3: 'Required',
        2: 'Recommended',
        1: 'Suggested'
    }

    # some default environment variables
    __default_dir_env_vars__ = {'cmip6_json': 'CMIP6_JSON_PATH'}

    def __init__(self):
        super(CMIP6CVBaseCheck, self).__init__()

    def check_cvs(self, ds):
        # get CV structure to check
        my_cv_structure = cv_structure(cv_tools.__cmip6_cv_struct_dict__)
        needed_cvs = my_cv_structure.get_cv_names_needed()

        # determine directory
        my_cv_directory_collection = data_directory_collection(
            self.__default_dir_env_vars__['cmip6_json'],
            self._cc_spec, 'cc')

        # update CVs if update necessary
        if my_cv_directory_collection.__do_update__:
            update_cmip6_json_cv(needed_cvs, my_cv_directory_collection)

        # get CVs
        cvs = read_cmip6_json_cv(needed_cvs, my_cv_directory_collection)
        # initialize further things
        results = []
        # Usage of `results` in the called functions:
        #   results.append([Result(BaseCheck.MEDIUM, check, 'blub', ['blab'])])
        results = self.iterate_cv_structure(results, ds, my_cv_structure, cvs)

        return results

    @accepts(None, list, nc._netCDF4.Dataset, cv_structure,
             cv_tools.__allowed_types_for_cvs__, list)
    def iterate_cv_structure(self, results, dataset, cv_struct, cvs,
                             parent_attribute_tree=[]):
        """
        @param dataset: netCDF4 file, opened
        """

        my_name = sys._getframe().f_code.co_name
        test_name_base_prefix = 'checking global attribute `'
        test_name_base_suffix = '` against CV'

        for attribute in cv_struct.get_attributes_to_check():
            test_name_base = (test_name_base_prefix + attribute +
                              test_name_base_suffix)
            this_attribute_tree = parent_attribute_tree.copy()
            this_attribute_tree.append(attribute)
            # print(attribute)
            # check value of attribute for presence in Dataset
            if (hasattr(dataset, attribute)):
                attr_correct = check_cv(cv_struct, attribute, cvs,
                                        getattr(dataset, attribute),
                                        guess=True)
                results.append(Result(BaseCheck.HIGH, attr_correct,
                                      test_name_base,
                                      ['attribute `' + attribute + '` with ' +
                                       'value "' +
                                       str(getattr(dataset, attribute)) +
                                       '" not present in CV; hierarchy of' +
                                       ' CVs checked: ' +
                                       ' -> '.join(this_attribute_tree)]))

                # check if:
                #   * there are attributes their values are somehow connected
                #      to the checked CV and
                #   * attr_correct is True => then we can extract child CVs
                if (cv_struct.has_children(attribute) and attr_correct):
                    # print('  has children!')
                    # obtain variables to parse to the children processing
                    cv_struct_child = cv_struct.get_children(attribute)
                    # get raw child CV; we still need to extract the actual
                    # child CV from it
                    if cv_struct.has_cv(attribute):
                        cvs_child_raw = cv_struct.get_cv(attribute)
                    else:
                        # get value of cv by `get` in order to provide default
                        cvs_child_raw = cvs.get(attribute, None)
                    # If the raw child cv we got is empty, then we skip
                    # checking this child.
                    if cvs_child_raw is None:
                        continue
                    # If the parent CV is not dictionary then we cannot extract
                    # child CVs from it.
                    if not isinstance(cvs_child_raw, dict):
                        raise TypeError(self._cc_spec + '.' + my_name + ': T' +
                                        'he provided cv_structure indicated ' +
                                        'that nested CVs (children) should b' +
                                        'e processed. However, the processed' +
                                        ' CV has to be of type `dict` in ord' +
                                        'er to be able to obtain child CVs f' +
                                        'rom it. The CV for checking attribu' +
                                        'te ' + attribute + ' is meant.')
                    # get actual child CV
                    cvs_child = cvs_child_raw[getattr(dataset, attribute)]

                    if (isinstance(cv_struct_child, cv_structure)):
                        # print('   child has cv_structure')
                        results = self.iterate_cv_structure(results, dataset,
                                                            cv_struct_child,
                                                            cvs_child,
                                                            this_attribute_tree
                                                            )
                    else:
                        # print('   child has no cv_structure')
                        if (should_process_all_cvs(cv_struct_child)):
                            results = self.iterate_cv_all(results, dataset,
                                                          cvs_child,
                                                          this_attribute_tree,
                                                          cv_tools.
                                                          __cmip6_cv_ignore__)

            else:
                results.append(Result(BaseCheck.HIGH, False, test_name_base,
                                      ['attribute `' + attribute + '` not ' +
                                       'present in netCDF file; hierarchy of' +
                                       ' CVs checked: ' +
                                       ' -> '.join(this_attribute_tree)]))

        return results

    @accepts(None, list, nc._netCDF4.Dataset,
             cv_tools.__allowed_types_for_cvs__, list, list)
    def iterate_cv_all(self, results, dataset, cvs,
                       parent_attribute_tree=[], ignore_cvs=[]):
        """
        @param dataset: netCDF4 file, opened
        """

        my_name = sys._getframe().f_code.co_name
        test_name_base_prefix = 'checking global attribute `'
        test_name_base_suffix = '` against CV'

        # The CVs have to be dictionaries. Otherwise, the automatic iteration
        # of the CVs does not work because one would not know which attribute
        # to check against each CV.
        if not isinstance(cvs, dict):
            raise TypeError(self._cc_spec + '.' + my_name + ': The CV(s) pro' +
                            'vided via argument `cvs` have to be of type `di' +
                            'ct`. Other types for CVs are not support by thi' +
                            's function.')

        # Generate a cv_struct from the keys of the dictionary
        autogen_cv_struct = cv_structure({attr: ['in', attr, None, '', False]
                                          for attr in cvs.keys()
                                          if attr not in ignore_cvs})

        # Iterate generated CV Structure; all `attributes` are in `cvs`
        # because we generated the cv_structure from the keys of `cvs`.
        for attribute in autogen_cv_struct.get_attributes_to_check():
            test_name_base = (test_name_base_prefix + attribute +
                              test_name_base_suffix)
            this_attribute_tree = parent_attribute_tree.copy()
            this_attribute_tree.append(attribute)
            # print(attribute)
            # check value of attribute for presence in Dataset
            if (hasattr(dataset, attribute)):
                attr_correct = check_cv(autogen_cv_struct, attribute, cvs,
                                        getattr(dataset, attribute),
                                        guess=True)
                results.append(Result(BaseCheck.HIGH, attr_correct,
                                      test_name_base,
                                      ['attribute `' + attribute + '` with ' +
                                       'value "' +
                                       str(getattr(dataset, attribute)) +
                                       '" not present in CV; hierarchy of' +
                                       ' CVs checked: ' +
                                       ' -> '.join(this_attribute_tree)]))

                # check if:
                #   * cvs[attribute] is a dict => we can get the value of key
                #                                 getattr(dataset, attribute)
                #   * attr_correct is True => then we can extract child CVs
                if (isinstance(cvs[attribute], dict) and attr_correct):
                    # print('  has children!')
                    # get child CV
                    cvs_child = cvs[attribute][getattr(dataset, attribute)]
                    # If the child cv we got is not a dict, we cannot
                    # proceed and skip checking this child.
                    if not isinstance(cvs_child, dict):
                        continue
                    
                    results = self.iterate_cv_all(results, dataset, cvs_child,
                                                  this_attribute_tree,
                                                  ignore_cvs)

            else:
                results.append(Result(BaseCheck.HIGH, False, test_name_base,
                                      ['attribute `' + attribute + '` not ' +
                                       'present in netCDF file; hierarchy of' +
                                       ' CVs checked: ' +
                                       ' -> '.join(this_attribute_tree)]))

        return results


class CMIP6CVNCCheck(BaseNCCheck, CMIP6CVBaseCheck):
    pass


class CMIP6CV_1_Check (CMIP6CVNCCheck):
    _cc_spec_version = '1.0'
    _cc_description = ('Checking global attributes against CMIP6 Controlled ' +
                       'Vocabulary')
    register_checker = True
