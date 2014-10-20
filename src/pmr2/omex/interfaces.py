import zope.interface
import zope.schema


class IOmexExposureArchiver(zope.interface.Interface):
    """
    Exposure archive class for generation of COMBINE archives.
    """

    def archive(exposure, path):
        """
        Use the manifest file specified by path to generate the archive.
        """
