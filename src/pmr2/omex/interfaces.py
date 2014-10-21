import zope.interface
import zope.schema


class IOmexNote(zope.interface.Interface):

    path = zope.schema.Text(
        title=u'Manifest path',
        description=u'The path to the Manifest file for this piece of work.',
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
