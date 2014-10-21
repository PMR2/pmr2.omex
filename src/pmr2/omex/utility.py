import zope.component
from zope.interface import implementer

from pmr2.app.annotation.interfaces import IExposureFileNote
from pmr2.app.workspace.interfaces import IStorageArchiver
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.exposure.interfaces import IExposureSourceAdapter

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
class OmexExposureFileArchiver(object):

    label = u'COMBINE Archive'
    suffix = '.omex'
    mimetype = 'application/vnd.combine.omex'

    def __init__(self, storage, path):
        self.storage = storage
        self.path = path

    def __call__(self):
        return build_omex(self.storage, self.path)


def OmexExposureArchiverFactory(exposure_object):
    # XXX only works with ExposureFile objects now.
    note = zope.component.getAdapter(exposure_object, name='omex')
    if note is None or note.path is None:
        return None

    try:
        exposure, workspace, path = zope.component.getAdapter(
            exposure_object, IExposureSourceAdapter).source()
        storage = IStorage(exposure)
        manifest = storage.file(path)
    except:
        return None

    archiver = OmexExposureFileArchiver(storage, note.path)
    return archiver
