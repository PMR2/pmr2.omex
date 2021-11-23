from __future__ import absolute_import

import urlparse

import zope.component
from zope.interface import implementer

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.api.pmr2.interfaces import ICellMLAPIUtility
from cellml.pmr2.urlopener import PmrUrlOpener
from cellml.pmr2.urlopener import make_pmr_path

# find all files in side the exposure, see if CellML/sedml


class LoggedPmrUrlOpener(PmrUrlOpener):

    def __init__(self):
        super(LoggedPmrUrlOpener, self).__init__()
        self.loaded = {}
        self.external = []
        # for ensuring that the recursive resolver only applies at the
        # outermost call.
        self.loading = False

    def loadURL(self, location, headers=None):
        p = urlparse.urlparse(location)
        # ensure that only the outermost caller is tracking the loaded
        # urls
        tracking = not self.loading
        if tracking and not p.scheme == 'pmr':
            tracking = False
            self.external.append(location)

        self.loading = True
        result = super(LoggedPmrUrlOpener, self).loadURL(location)
        if tracking:
            self.loading = False
            self.loaded[location] = result
        return result


class TrackedCellMLLoader(object):

    def load(self, exposure_file, urlopener=None):
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
        urlopener = urlopener or LoggedPmrUrlOpener()
        model = cu.loadModel(target, loader=urlopener)
        # the map of loaded modules
        return {
            key[len(root):]: value
            for key, value in urlopener.loaded.items()
            if key.startswith(root)
        }
