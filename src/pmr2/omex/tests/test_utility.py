from unittest import TestCase, TestSuite, makeSuite

import zope.component

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageArchiver

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
        # this one has the annotation to the path of manifest file.
        self.ef_with_omex = self.portal.ec.combine_test['demo.xml']
        # this one has no annotation with path to manifest file.
        self.ef_no_omex = self.portal.ec.combine_test['no_omex.xml']

    def tearDown(self):
        pass

    def test_generate_omex_ef_with_omex(self):
        archiver = zope.component.getAdapter(self.ef_with_omex,
            IOmexExposureArchiver)
        result = archiver()
        # XXX figure out how to grab this.
        self.assertEqual(result.filelist,
            ['with_omex_manifest.xml', 'with_omex.xml'])

    def test_generate_omex_ef_no_omex(self):
        # no archiver available.
        archiver = zope.component.queryAdapter(self.ef_no_omex,
            IOmexExposureArchiver)
        self.assertIsNone(archiver)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOmexStorageUtility))
    suite.addTest(makeSuite(TestOmexExposureUtility))
    return suite

