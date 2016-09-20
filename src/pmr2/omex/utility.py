from functools import partial

import zope.component
from zope.interface import implementer

from pmr2.app.annotation.interfaces import IExposureFileNote
from pmr2.app.workspace.interfaces import IStorageArchiver
from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.exposure.interfaces import IExposureSourceAdapter
from pmr2.app.exposure.interfaces import IExposureDownloadTool
from pmr2.app.exposure.interfaces import IExposureFileTool

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


@implementer(IExposureDownloadTool)
class OmexExposureDownloadTool(object):
    """
    COMBINE Archive Download tool.
    """

    label = u'COMBINE Archive'
    suffix = '.omex'
    mimetype = 'application/vnd.combine.omex'

    def get_download_link(self, exposure_object):
        archiver = zope.component.queryAdapter(
            exposure_object, IOmexExposureArchiver)
        if archiver:
            return exposure_object.absolute_url() + '/download_omex'

    def download(self, exposure_object, request):
        archiver = zope.component.queryAdapter(
            exposure_object, IOmexExposureArchiver)
        if archiver:
            return archiver()


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

    archiver = partial(build_omex, storage, note.path)
    return archiver


@implementer(IExposureFileTool)
class WebCatLinkTool(object):
    """
    Linkage to external webcat tool.
    """

    label = u'CombineArchive Web'

    def get_tool_link(self, exposure_object):
        try:
            exposure, workspace, path = zope.component.getAdapter(
                exposure_object, IExposureSourceAdapter).source()
        except:
            return None

        return exposure.absolute_url() + '/webcat_tool'
