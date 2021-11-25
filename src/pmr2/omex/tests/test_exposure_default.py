from unittest import TestCase
from zope.component import getUtility

from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.testing.layer import OMEX_EXPOSURE_INTEGRATION_LAYER


class LoaderTestCase(TestCase):

    layer = OMEX_EXPOSURE_INTEGRATION_LAYER

    def test_extract_single(self):
        loader = getUtility(IExposureFileLoader)
        exposure_file = self.layer['portal'].ec.combine_test0['demo.xml']
        result = sorted(loader.load(exposure_file).keys())
        self.assertEqual([
            'demo.xml'
        ], result)
