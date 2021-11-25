from __future__ import absolute_import

import urlparse

import zope.component
from zope.interface import implementer

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.api.pmr2.interfaces import ICellMLAPIUtility
from cellml.api.pmr2.interfaces import CellMLLoaderError
from cellml.pmr2.urlopener import make_pmr_path

from pmr2.omex.exposure.interfaces import DuplicateURLError
from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener
from pmr2.omex.exposure.default import ExposureFileLoader


@implementer(IExposureFileLoader)
class TrackedCellMLLoader(ExposureFileLoader):

    def loadTarget(self, urn, urlopener):
        cu = zope.component.getUtility(ICellMLAPIUtility)
        try:
            cu.loadModel(urn, loader=urlopener)
        except (DuplicateURLError, CellMLLoaderError):
            # we only care that the model and its imports are loaded at
            # least once nor do we care if the model is invalid...
            pass
