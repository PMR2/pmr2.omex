import zope.interface
import zope.schema

from pmr2.app.workspace.schema import StorageFileChoice


class IOmexNote(zope.interface.Interface):

    path = StorageFileChoice(
        title=u'Manifest path',
        description=u'The path to the Manifest file for this piece of work.',
        vocabulary='pmr2.vocab.manifest',
        required=False,
    )


class IOmexExposureArchiver(zope.interface.Interface):
    """
    Exposure archive class for generation of COMBINE archives.
    """

    def archive(exposure, path):
        """
        Use the manifest file specified by path to generate the archive.
        """
