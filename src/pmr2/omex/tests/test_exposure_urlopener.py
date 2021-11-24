from unittest import TestCase, TestSuite, makeSuite
from io import BytesIO

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.exposure.browser.browser import ExposureAddForm
from pmr2.app.exposure.browser.browser import ExposureFileGenForm
from pmr2.testing.base import TestRequest

from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener

from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER


class UrlOpenerTestCase(TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_open_default(self):
        exposure_file = self.layer['portal'].unrestrictedTraverse(
            self.layer['exposure_file1_path'])
        opener = LoggedPmrUrlOpener()
        result = opener.loadURL(
            'pmr:/plone/workspace/demo_model:0:/multi.cellml')
        self.assertEqual({
            'pmr:/plone/workspace/demo_model:0:/multi.cellml': result,
        }, opener.loaded)

    def test_open_embedded(self):
        registry = getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}

        exposure_file = self.layer['portal'].unrestrictedTraverse(
            self.layer['exposure_file1_path'])
        opener = LoggedPmrUrlOpener()
        result = opener.loadURL(
            'pmr:/plone/workspace/demo_model:0:/main/model.cellml')
        self.assertEqual({
            'pmr:/plone/workspace/demo_model:0:/main/model.cellml': result,
        }, opener.loaded)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(UrlOpenerTestCase))
    return suite
