from unittest import TestCase

import zipfile
from io import BytesIO

from zope.component import getUtility

from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.utility import ExposureGeneratedOmexArchiver

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

    def test_default_archive(self):
        archiver = ExposureGeneratedOmexArchiver()
        zipbytes = archiver.archive_exposure(
            self.layer['portal'].ec.combine_test0)
        zf = zipfile.ZipFile(BytesIO(zipbytes), mode='r')
        self.assertEqual([
            '!!autogen-disclaimer.txt',
            'demo.xml',
            'manifest.xml',
            'no_omex.xml',
        ], sorted(zf.namelist()))
