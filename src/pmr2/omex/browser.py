import zope.component
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from pmr2.z3cform.page import SimplePage
from pmr2.app.workspace.exceptions import StorageArchiveError
from pmr2.app.exposure.interfaces import IExposureDownloadTool


class OmexErrorPage(SimplePage):

    template = ViewPageTemplateFile('omex_error.pt')
    source = ''
    manifest = ''


class OmexExposureDownload(BrowserView):
    """
    COMBINE Archive Download tool.
    """

    # XXX this can actually be made into a generic one.

    def __call__(self):
        # XXX replace name with self.__name__ perhaps?
        tool = zope.component.getUtility(IExposureDownloadTool, name='omex')
        try:
            content = tool.download(self.context, self.request)
        except StorageArchiveError as e:
            # XXX assume only successful acquisition of the note will
            # result in a codepath that takes us to one where this
            # exception gets raised.
            note = zope.component.getAdapter(self.context, name='omex')
            p = OmexErrorPage(self.context, self.request)
            p.source = e.message
            p.manifest = note.path
            return p()
        if content is None:
            raise NotFound(self.context, 'download_omex')
        self.request.response.setHeader('Content-Type', tool.mimetype)
        self.request.response.setHeader('Content-Length', len(content))
        self.request.response.setHeader('Content-Disposition',
            'attachment; filename="%s%s"' % (self.context.id, tool.suffix))
        return content


