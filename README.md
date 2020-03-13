# CMIP6 Controlled Vocabulary Checker Plugin for the IOOS Compliance Checker

This plugin is meant to check the global attributes of netCDF files for the conformance with the CMIP6 standard. The global attributes are checked against controlled vocabularies (CVs). Other things like the coordinates system within the netCDF files, the CF Conventions or the DRS are not checked. Compliance with the CF Conventions has to be checked with the CF Conventions Plugin.

If you deploy this Plugin in a multi-user environment (e.g. a HPC system) you might consider to place the CVs at a central location and let the user's environement variable `CMIP6_JSON_PATH` point to the location. See further below for details.

This Plugin is made in a way that several functions can be reused when `things` (texts, global attributes, variable names, ...) should be checked against other controlled vocabularies. There is a structure `__cmip6_cv_struct_dict__` defined in `cv_tools` from which an instance of `cv_structure` is generated. The resulting object holds information on how the `things` are compared against the CVs.

Useful links:

* This plugin's repository: https://github.com/neumannd/cc-plugin-cmip6-cv
* IOOS Compliance Checker repository: https://github.com/ioos/compliance-checker
* CMIP6 CV repository: https://github.com/WCRP-CMIP/CMIP6_CVs


## Installation

### Conda

**not available yet; later it will be:**

```shell
$ conda install -c conda-forge cc-plugin-cmip6-cv
```

### Pip, Precompiled

**not available yet**


### Pip, own compilation (e.g. for development)

```shell
python setup.py develop
```

Uninstall before new install:

```shell
pip uninstall cc-plugin-cmip6-cv
```



## Usage

```shell
$ compliance-checker -l
IOOS compliance checker available checker suites (code version):
  ...
  - cmip6_cv (x.x.x)
  ...
$ compliance-checker -t cmip6_cv [dataset_location]
```

See the [ioos/compliance-checker](https://github.com/ioos/compliance-checker) for additional Usage notes


## Summary of the Checks

...

### High priority checks
Failures in these checks should be addressed before submitting within AtMoDat!

- `check_cvs`


### Medium priority checks:

- currently none


### Low priority checks

- currently none


## Optional environment variables

The path of existing CMIP6 JSON controlled vocabulary (CV) files can be provided explicitly via:

* `CMIP6_JSON_PATH`

Please see the notes below


## Locations and update of CMIP6 controlled vocabularies

**tldr;**: Please look into the table below for a quick overview over where CVs are expected and when/if they are updated.

Controlled vocabularies (CV) are imported from the official CMIP6 CV files. These are JSON files.

This plugin contains its own set of CMIP6 CV files. They might be outdated in future. By default, the plugin looks in into the user's home folder for CV files. If they exist, the plugin tries to update them if the last update was performed more than 7 days ago (`cc_plugin_cmip6_cv.util.__update_period__`).

Priority | Location | Download new version (if possible)
---------|----------|-----------------------------------
1        | `$CMIP6_JSON_PATH` | no
2        | `appdirs.user_data_dir(cc_plugin_cmip6_cv.cmip6_cv.CMIP6BaseCheck.__cc_spec, 'cc')` | yes
3        | `"PACKAGE INSTALLATION DIRECTORY"/cc_plugin_cmip6/data` | no

**Note:** `cc_plugin_cmip6_cv.CMIP6BaseCheck.__cc_spec` does probably have the value `cmip6`. However, this might change.


## Web locations of controlled vocabularies

Type of file(s) | Remote Table Location
-------------------- | ---------------------
CMIP6 CVs | https://raw.githubusercontent.com/WCRP-CMIP/CMIP6_CVs/master


## Notes for Developers

### userful variables

Variable | Default | Description
---------|---------|------------
`cc_plugin_cmip6_cv.util.__update_period__` | 7 days | time period during which no updates of the CVs are performed
`cc_plugin_cmip6_cv.util.__data_url__` | *too long* | download location for CMIP6 CV json files
`cc_plugin_cmip6_cv.cv_tools.__cmip6_cv_struct_dict__` | *too long* | description of how to process the CVs (see `cc_plugin_cmip6_cv.cmip6_cv.CMIP6BaseCheck` for usage example); **this is a core element**
`cc_plugin_cmip6_cv.cv_tools.__allowed_types_for_cvs__` | *too long* | CVs are allowed to be of these types
`cc_plugin_cmip6_cv.cv_tools.cv_structure.__allowed_operations__` | *too long* | implemented/allowed operations to compare global attributes against CVs
`cc_plugin_cmip6_cv.cv_tools.cv_structure.__allowed_cv_preproc_funs__` | *too long* | list of allowed functions for preprocessing of CVs (see further below for details)
`cc_plugin_cmip6_cv.cmip6_cv.CMIP6BaseCheck.__default_dir_env_vars__` | *too long* | holds names of environment that might be checked for user input

### Notes on the usage of CVs

Some CVs are provided as `dict`ionaries. Some global attributes are compared against the `key`s of these `dict`ionaries and others are compared agains the `value`s of these `dict`ionaries. The instance of the class `cv_structure` contains information what should be done. We did define this in a general sense: the user provides a function name; this name is looked up in a list of allowed functions; a function returns a `callable` corresponding to the provided name; this is hard-coded to prevent code injection; the returned callable is called with associated CV as input.

To generate a proper instance of `cv_structure` for the current CMIP6 CVs one should instanciate it with `cc_plugin_cmip6_cv.cv_tools.__cmip6_cv_struct_dict__`. This variable is also a good example on how to adapt this plugin for checking other CVs.


## Contributors

## Direct Contributors

### Indirect Contributors via Stackexchange Network

* user [sacuL](https://stackoverflow.com/users/6671176/sacul) in post https://stackoverflow.com/a/53527901/4612235
* use [jfs](https://stackoverflow.com/users/4279/jfs) in post https://stackoverflow.com/a/15300191/4612235
* https://stackoverflow.com/a/53527901/4612235
* general on decorators:
   * https://stackoverflow.com/questions/15299878/how-to-use-python-decorators-to-check-function-arguments
   * https://realpython.com/primer-on-python-decorators/
   * https://wiki.python.org/moin/PythonDecorators
   * https://dev.to/apcelent/python-decorator-tutorial-with-example-529f
* processing of `**kwargs`:
   * http://www.informit.com/articles/article.aspx?p=2314818
   * https://stackoverflow.com/questions/53128068/keyerror-in-python-kwargs
* get name of current function
   * https://www.oreilly.com/library/view/python-cookbook/0596001673/ch14s08.html
   * https://stackoverflow.com/q/5067604/4612235
   * `sys._getframe().f_code.co_name`
* extract n'th element of dict
   * https://stackoverflow.com/questions/16977385/extract-the-nth-key-in-a-python-dictionary/16977485
   * https://stackoverflow.com/questions/16819222/how-to-return-dictionary-keys-as-a-list-in-python
   * or `next(iter(dict.keys()))`
* inspect functions signature
   * https://www.programcreek.com/python/example/81294/inspect.signature
* Test Docrators
   * https://stackoverflow.com/questions/34648337/how-to-test-a-decorator-in-a-python-package/34648674




