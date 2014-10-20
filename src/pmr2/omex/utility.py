import zope.component
from zope.interface import implementer

from pmr2.app.workspace.interfaces import IStorageArchiver
from pmr2.app.workspace.interfaces import IStorage

from .interfaces import IOmexExposureArchiver
from .omex import build_omex


@implementer(IStorageArchiver)
class OmexStorageArchiver(object):

    label = u'COMBINE Archive'
    suffix = '.omex'
    mimetype = 'application/vnd.combine.omex'

    def enabledFor(self, storage):
        try:
            manifest = storage.file('manifest.xml')
            return True
        except:
            return False

    def archive(self, storage):
        return build_omex(storage)


@implementer(IOmexExposureArchiver)
class OmexExposureArchiver(object):

    label = u'COMBINE Archive'
    suffix = '.omex'
    mimetype = 'application/vnd.combine.omex'

    def enabledFor(self, exposure_object, path=None):
        storage = IStorage(exposure_object)
        try:
            # XXX path can be either default to like workspace, or have
            # some other adapter that provide this info.
            manifest = storage.file(path)
            return True
        except:
            return False

    def archive(self, exposure):
        storage = IStorage(exposure_object)
        return build_omex(storage)
