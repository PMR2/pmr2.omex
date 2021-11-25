from __future__ import absolute_import

import zope.component
from zope.interface import implementer

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.pmr2.urlopener import make_pmr_path

from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.interfaces import DuplicateURLError
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener


@implementer(IExposureFileLoader)
class ExposureFileLoader(object):

    def load(self, exposure_file, urlopener=None):
        urlopener = urlopener or LoggedPmrUrlOpener()
        sa = zope.component.getAdapter(exposure_file, IExposureSourceAdapter)
        # rather than processing the file directly, let the urlopener
        # track the process
        exposure, workspace, path = sa.source()
        # need this to resolve.
        root = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, '')
        urn = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, path)
        self.loadTarget(urn, urlopener)

        return {
            key[len(root):]: value
            for key, value in urlopener.loaded.items()
            if key.startswith(root)
        }

    def loadTarget(self, urn, urlopener):
        try:
            return urlopener.loadURL(urn)
        except DuplicateURLError:
            pass
