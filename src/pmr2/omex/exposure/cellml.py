from __future__ import absolute_import

import urlparse

import zope.component
from zope.interface import implementer

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.api.pmr2.interfaces import ICellMLAPIUtility
from cellml.pmr2.urlopener import make_pmr_path

from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener


@implementer(IExposureFileLoader)
class TrackedCellMLLoader(object):

    def load(self, exposure_file, urlopener=None):
        urlopener = urlopener or LoggedPmrUrlOpener()
        cu = zope.component.getUtility(ICellMLAPIUtility)
        sa = zope.component.getAdapter(exposure_file, IExposureSourceAdapter)
        exposure, workspace, path = sa.source()
        modelfile = '%s/@@%s/%s/%s' % (workspace.absolute_url(),
            'rawfile', exposure.commit_id, path)
        # need this to resolve.
        root = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, '')
        target = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, path)
        model = cu.loadModel(target, loader=urlopener)
        # the map of loaded modules
        return {
            key[len(root):]: value
            for key, value in urlopener.loaded.items()
            if key.startswith(root)
        }
