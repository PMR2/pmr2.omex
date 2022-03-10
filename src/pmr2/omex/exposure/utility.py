from __future__ import absolute_import

from os.path import splitext
from zope.component import getUtility, queryUtility, getAdapter
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from cellml.pmr2.urlopener import make_pmr_path
from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener
from pmr2.omex.omex import generate_manifest, _create_zip

exposure_autogenerated_warning = """\
This OMEX archive is automatically generated from the selected exposure,
using resources that have been manually exposed, along with any known
linked resources (examples: SED-ML files will pull in all referenced
resources; CellML 1.1 files will pull in their imports through embedded
workspaces on the same PMR instance).

Any resources present in the source workspace but not linked are omitted
from this OMEX archive.

However, if a file is expected to be present in this archive but was
omitted, checked whether or not the source exposure has exposed that
file, if not, you may file an issue at:

https://github.com/PMR2/models.physiomeproject.org/issues

Alternatively, if this missing resource is present but somehow unlinked,
it could be that the export system has no knowledge on how that linkage
might be handled, in which case, please file an issue at:

https://github.com/PMR2/pmr2.omex/issues
"""


class ExposureGeneratedOmexArchiver(object):
    """
    The exposure to omex archive builder.
    """

    def process_exposure_file(self, exposure_file, urlopener):
        """
        Resolve the correct helper with the exposure file.
        """

        extname = splitext(exposure_file.getPhysicalPath()[-1])[1][1:]
        utility = queryUtility(
            IExposureFileLoader, name=extname,
            default=getUtility(IExposureFileLoader)
        )
        utility.load(exposure_file, urlopener)

    def archive_exposure(self, exposure):
        urlopener = LoggedPmrUrlOpener()
        catalog = getToolByName(exposure, 'portal_catalog')
        path = '/'.join(exposure.getPhysicalPath())
        for target in catalog(path=path, portal_type="ExposureFile"):
            self.process_exposure_file(target.getObject(), urlopener)

        # process urlopener data into archive
        filemap = {
            '.': '',  # placeholder for parent entry
            '!!autogen-disclaimer.txt': exposure_autogenerated_warning,
        }
        # TODO figure out how to refactor this chunk of copypasta code
        # needed in various places.
        sa = getAdapter(exposure, IExposureSourceAdapter)
        exposure, workspace, path = sa.source()
        root = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, '')
        filemap.update({
            key[len(root):]: value
            for key, value in urlopener.loaded.items()
            if key.startswith(root)
        })
        filemap['manifest.xml'] = generate_manifest(filemap)
        return _create_zip(filemap.items())
