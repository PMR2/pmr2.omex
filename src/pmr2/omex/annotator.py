import zope.interface
import zope.component

from pmr2.app.factory import named_factory
from pmr2.app.annotation.interfaces import IExposureFileEditAnnotator
from pmr2.app.annotation.annotator import ExposureFileAnnotatorBase
from pmr2.app.annotation.annotator import PortalTransformAnnotatorBase

from pmr2.omex.interfaces import IOmexNote


@zope.interface.implementer(IExposureFileEditAnnotator)
class OmexAnnotator(ExposureFileAnnotatorBase):
    title = u'COMBINE Archive Path'
    label = u'COMBINE Archive'
    description = u''
    for_interface = IOmexNote

OmexAnnotatorFactory = named_factory(OmexAnnotator)
