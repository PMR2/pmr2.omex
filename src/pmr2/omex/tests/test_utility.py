from unittest import TestCase, TestSuite, makeSuite

import zope.component

from pmr2.app.workspace.interfaces import IStorage
from pmr2.app.workspace.interfaces import IStorageArchiver

from pmr2.omex.testing.layer import OMEX_BASE_INTEGRATION_LAYER


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


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOmexStorageUtility))
    return suite

