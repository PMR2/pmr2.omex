from __future__ import absolute_import

from os.path import splitext
from zope.component import getUtility, queryUtility, getAdapter
from Products.CMFCore.utils import getToolByName

from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from cellml.pmr2.urlopener import make_pmr_path
from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener
from pmr2.omex.omex import generate_manifest, _create_zip


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
