import zope.interface
import zope.schema

from pmr2.app.workspace.schema import StorageFileChoice


class IOmexNote(zope.interface.Interface):

    path = StorageFileChoice(
        title=u'Manifest path',
        description=u'The path to the COMBINE manifest file that specifies '
                     'the files relating to this piece of work.  If a valid '
                     'manifest file is specified, a "COMBINE Archive" '
                     'download link will be enabled for this exposure file.',
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
