from unittest import TestCase, TestSuite, makeSuite
from io import BytesIO

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.exposure.browser.browser import ExposureAddForm
from pmr2.app.exposure.browser.browser import ExposureFileGenForm
from pmr2.testing.base import TestRequest

from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener
from pmr2.omex.exposure.cellml import TrackedCellMLLoader

from cellml.pmr2.tests.layer import CELLML_EXPOSURE_INTEGRATION_LAYER


class LoaderTestCase(TestCase):

    layer = CELLML_EXPOSURE_INTEGRATION_LAYER

    def test_extract_single(self):
        exposure_file = self.layer['portal'].unrestrictedTraverse(
            self.layer['exposure_file1_path'])
        loader = TrackedCellMLLoader()
        result = sorted(loader.load(exposure_file).keys())
        self.assertEqual([
            'example_model.cellml'
        ], result)

    def test_extract_embeded_workspace_standard(self):
        request = TestRequest(form={
            'form.widgets.workspace': u'demo_model',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]
        request = TestRequest(form={
            'form.widgets.filename': [u'multi.cellml'],
            'form.buttons.add': 1,
        })
        testform = ExposureFileGenForm(context, request)
        testform.update()
        exposure_file = context[u'multi.cellml']
        registry = getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}

        loader = TrackedCellMLLoader()
        result = sorted(loader.load(exposure_file).keys())

        self.assertEqual([
            u'main/model.cellml',
            u'multi.cellml',
        ], result)

    def test_extract_embeded_workspace_mixed_external(self):
        # inject a modified version of the multi2 model
        su = getUtility(IStorageUtility, name='dummy_storage')
        src = su._dummy_storage_data['demo_model'][0]['multi.cellml']
        lines = src.splitlines(True)
        su._dummy_storage_data['demo_model'][0]['multi2.cellml'] = (
            ''.join(lines[:19]) +
            # modification involves a valid external import URI
            lines[19].replace('href="', 'href="http://models.example.com/') +
            ''.join(lines[20:])
        )

        # patch urllib2.urlopen to return this exact result
        def urlopen(*a, **kw):
            return BytesIO(
                su._dummy_storage_data['main_model'][0]['model.cellml'])

        import urllib2
        urllib2_urlopen, urllib2.urlopen = urllib2.urlopen, urlopen

        def cleanup():
            urllib2.urlopen = urllib2_urlopen

        self.addCleanup(cleanup)

        request = TestRequest(form={
            'form.widgets.workspace': u'demo_model',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]
        request = TestRequest(form={
            'form.widgets.filename': [u'multi2.cellml'],
            'form.buttons.add': 1,
        })
        testform = ExposureFileGenForm(context, request)
        testform.update()
        exposure_file = context[u'multi2.cellml']
        registry = getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}

        loader = TrackedCellMLLoader()
        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        self.assertEqual([
            u'main/model.cellml',
            u'multi2.cellml',
        ], result)
        self.assertEqual([
            'http://models.example.com/main/model.cellml',
        ], urlopener.external)

    def test_extract_embeded_workspace_missing_registry(self):
        su = getUtility(IStorageUtility, name='dummy_storage')
        src = su._dummy_storage_data['demo_model'][0]['multi.cellml']

        loaded = []

        # patch urllib2.urlopen to return this exact result
        def urlopen(request):
            loaded.append(request.get_full_url())
            return BytesIO(
                su._dummy_storage_data['main_model'][0]['model.cellml'])

        import urllib2
        urllib2_urlopen, urllib2.urlopen = urllib2.urlopen, urlopen

        def cleanup():
            urllib2.urlopen = urllib2_urlopen

        self.addCleanup(cleanup)

        request = TestRequest(form={
            'form.widgets.workspace': u'demo_model',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]
        request = TestRequest(form={
            'form.widgets.filename': [u'multi.cellml'],
            'form.buttons.add': 1,
        })
        testform = ExposureFileGenForm(context, request)
        testform.update()
        exposure_file = context[u'multi.cellml']

        loader = TrackedCellMLLoader()
        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        self.assertEqual([
            u'main/model.cellml',
            u'multi.cellml',
        ], result)
        # external is only measured if directly linked via absolute URIs
        self.assertEqual([], urlopener.external)
        # relative references through externally defined repositories
        # will still be loaded.
        self.assertEqual([
            'http://nohost/plone/workspace/main_model/rawfile/0/model.cellml',
            'http://nohost/plone/workspace/main_model/rawfile/0/model.cellml',
            'http://nohost/plone/workspace/main_model/rawfile/0/model.cellml',
        ], loaded)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(LoaderTestCase))
    return suite
