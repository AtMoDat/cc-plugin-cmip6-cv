# ~~~~~~~~~~~~~~ imports ~~~~~~~~~~~~~~
import numpy


# ~~~~~~~~~~~~~~ constants ~~~~~~~~~~~~~~
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