Changelog
=========

0.5.0 - Released (2022-05-18)
-----------------------------

- Correct the implementation for exposure file notes from views, as that
  is where the data is ultimately stored
- Correct the implementation of the target for the OpenCOR simulation
  link.

0.4.0 - Released (2022-03-14)
-----------------------------

- Provide a means to include resources links or references present in
  exposure file views, and now include a disclaimer.

0.3.0 - Released (2021-12-01)
-----------------------------

- Generate omex archives from an exposure, provides an initial hard-
  coded support for CellML and SED-ML exposure files for resolving
  linked resources.

0.2.2 - Released (2017-09-20)
-----------------------------

- Provide external_attr to the zipfile info bits so that tools that make
  use of these data don't trigger permission errors.

0.2.1 - Released (2016-12-29)
-----------------------------

- Minor text fixes

0.2 - Released (2016-11-29)
---------------------------

- Support the self-reference (by not generating a file entry)
- Support for generation of archives through self-reference into
  embedded workspaces.

0.1 - Released (2015-03-19)
---------------------------

- Addon to PMR2 for the creation of COMBINE Archive from exposures
- Also includes the functionality of generation of COMBINE Archive from
  workspaces.
