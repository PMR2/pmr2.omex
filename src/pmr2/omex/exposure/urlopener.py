from __future__ import absolute_import

import urlparse

import zope.component
from zope.interface import implementer

from cellml.pmr2.urlopener import PmrUrlOpener


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
