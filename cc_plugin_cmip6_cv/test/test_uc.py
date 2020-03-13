# load packages
from __future__ import (absolute_import, division, print_function)
from cc_plugin_cmip6_cv.cmip6_cv import CMIP6CVBaseCheck
from compliance_checker import MemoizedDataset

# data path
# path = "../../../cc_plugin_cmip6_cv/test/data/"
path = "cc_plugin_cmip6_cv/test/data/"

# load data set
ds_str = path+'example_file_cf_issue_212.nc'
ds = MemoizedDataset(ds_str)

# initialize checker
my_checker = CMIP6CVBaseCheck()

# test a function
my_checker.check_cvs(ds)
