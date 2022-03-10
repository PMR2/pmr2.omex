from __future__ import absolute_import

from urllib2 import URLError
import zope.interface

from cellml.api.pmr2.interfaces import CellMLLoaderError


class DuplicateURLError(URLError):
    """
    For signaling an abort on a duplicate URL to be loaded.
    """


class IExposureFileLoader(zope.interface.Interface):

    def load(exposure_file, urlopener=None):
        """
        Load the provided exposure file and produce a mapping of all
        loaded files; takes an optional urlopener that would provide the
        logged loaded field.
        """

    def loadTarget(urn, urlopener):
        """
        Load the provided urn with the urlopener in order to register
        the urn with the urlopener
        """


class IExposureFileViewHandler(zope.interface.Interface):

    def handle(view, urlopener):
        """
        Handle the view with the urlopener.

        This is typically called from the ExposureFileLoader.load()
        method.
        """
