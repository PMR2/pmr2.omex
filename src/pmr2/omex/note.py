import zope.interface
import zope.component
from zope.schema import fieldproperty
    
from pmr2.app.annotation.interfaces import IExposureFileEditableNote
from pmr2.app.annotation.note import ExposureFileEditableNoteBase
from pmr2.app.annotation import note_factory
      
from pmr2.omex.interfaces import IOmexNote
      
      
class OmexNote(ExposureFileEditableNoteBase):
  
    zope.interface.implements(IOmexNote, IExposureFileEditableNote)
      
    path = fieldproperty.FieldProperty(IOmexNote['path'])
    
OmexNoteFactory = note_factory(OmexNote, 'omex')
