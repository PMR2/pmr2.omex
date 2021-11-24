import zope.interface


class IExposureFileLoader(zope.interface.Interface):

    def load(exposure_file, urlopener=None):
        """
        Load the provided exposure file and produce a mapping of all
        loaded files; takes an optional urlopener that would provide the
        logged loaded field.
        """
