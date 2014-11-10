from unittest import TestCase, TestSuite, makeSuite

from cStringIO import StringIO
import zipfile

import zope.component

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageArchiver
from pmr2.app.workspace.exceptions import StorageArchiveError

from pmr2.app.exposure.browser.browser import ExposureFileAnnotatorForm
from pmr2.app.exposure.browser.browser import ExposureFileNoteEditForm
from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.app.annotation.interfaces import IExposureFileAnnotator

from pmr2.testing.base import TestRequest

from pmr2.omex.browser import OmexExposureDownload
from pmr2.omex.interfaces import IOmexExposureArchiver

from pmr2.omex.testing.layer import OMEX_BASE_INTEGRATION_LAYER
from pmr2.omex.testing.layer import OMEX_EXPOSURE_INTEGRATION_LAYER

class TestOmexStorageUtility(TestCase):
    """
    Test Omex Core.
    """

    layer = OMEX_BASE_INTEGRATION_LAYER

    def setUp(self):
        # get a dummy exposure with some data.
        self.portal = self.layer['portal']

    def tearDown(self):
        pass

    def test_utility_base(self):
        utility = zope.component.getUtility(IStorageArchiver, name='omex')
        self.assertFalse(utility.enabledFor(
            IStorage(self.portal.workspace.test)))

        target = IStorage(self.portal.workspace.omex_base)
        self.assertFalse(utility.enabledFor(target))

        # on the revision with the root manifest.xml
        target.checkout('0')
        self.assertTrue(utility.enabledFor(target))


class TestOmexExposureUtility(TestCase):
    """
    Test Omex Core.
    """

    layer = OMEX_EXPOSURE_INTEGRATION_LAYER

    def setUp(self):
        # get a dummy exposure with some data.

        self.portal = self.layer['portal']
        self.exposure = self.portal.ec.combine_test
        self.exposure1 = self.portal.ec.combine_test1
        # this one has the annotation to the path of manifest file.
        self.ef_with_omex = self.portal.ec.combine_test['demo.xml']
        # this one has no annotation with path to manifest file.
        self.ef_no_omex = self.portal.ec.combine_test['no_omex.xml']

        self.ef_broken_manifest = self.portal.ec.combine_test1['demo.xml']

    def tearDown(self):
        pass

    def test_generate_omex_ef_with_omex(self):
        context = self.ef_with_omex
        request = TestRequest()
        annotator = zope.component.getUtility(IExposureFileAnnotator,
            name='omex')(context, request)
        annotator(data=(('path', u'demo_only.xml'),))

        archiver = zope.component.getAdapter(context, IOmexExposureArchiver)
        result = archiver()

        stream = StringIO(result)
        zf = zipfile.ZipFile(stream, mode='r')

        self.assertEqual(sorted(zf.namelist()),
            ['demo.xml', 'demo_only.xml'])

        # run again with the view.
        dl = OmexExposureDownload(context, request)
        result = dl()
        stream = StringIO(result)
        zf = zipfile.ZipFile(stream, mode='r')
        self.assertEqual(sorted(zf.namelist()),
            ['demo.xml', 'demo_only.xml'])

    def test_generate_omex_ef_no_omex(self):
        # no archiver available.
        archiver = zope.component.queryAdapter(self.ef_no_omex,
            IOmexExposureArchiver)
        self.assertIsNone(archiver)

    def test_generate_omex_ef_manifest_missing_file(self):
        context = self.ef_broken_manifest
        request = TestRequest()
        annotator = zope.component.getUtility(IExposureFileAnnotator,
            name='omex')(context, request)
        annotator(data=(('path', u'all_manifest.xml'),))

        archiver = zope.component.getAdapter(context, IOmexExposureArchiver)
        self.assertRaises(StorageArchiveError, archiver)

        dl = OmexExposureDownload(context, request)
        result = dl()

        self.assertTrue('Error' in result)
        self.assertTrue('manifest.xml' in result)
        self.assertTrue('all_manifest.xml' in result)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOmexStorageUtility))
    suite.addTest(makeSuite(TestOmexExposureUtility))
    return suite

