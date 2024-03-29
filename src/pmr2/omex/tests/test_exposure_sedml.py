import unittest
import zipfile
from io import BytesIO

from zope.component import getUtility
from zope.component import queryAdapter
from plone.registry.interfaces import IRegistry

from pmr2.app.annotation.factory import has_note
from pmr2.app.workspace.interfaces import IStorageUtility
from pmr2.app.exposure.browser.browser import ExposureAddForm
from pmr2.app.exposure.browser.browser import ExposureFileGenForm

from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener
from pmr2.omex.exposure.default import ExposureFileLoader
from pmr2.omex.exposure.sedml import TrackedSedMLLoader
from pmr2.omex.exposure.utility import ExposureGeneratedOmexArchiver

from pmr2.testing.base import TestRequest
from plone.app.testing import IntegrationTesting
from cellml.pmr2.tests.layer import CELLML_EXPOSURE_FIXTURE
from pmr2.omex.testing.layer import OMEX_EXPOSURE_FIXTURE

SEDML_INTEGRATION_LAYER = IntegrationTesting(
    bases=(CELLML_EXPOSURE_FIXTURE, OMEX_EXPOSURE_FIXTURE,),
    name="pmr2.omex:sedml_integration"
)


class SedMLTestCase(unittest.TestCase):

    layer = SEDML_INTEGRATION_LAYER

    def test_simple(self):
        request = TestRequest(form={
            'form.widgets.workspace': u'sedml',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]

        ExposureFileGenForm(context, TestRequest(form={
            'form.widgets.filename': [u'simple.sedml'],
            'form.buttons.add': 1,
        })).update()

        exposure_file = context[u'simple.sedml']
        loader = TrackedSedMLLoader()
        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        self.assertEqual([
            u'demo.cellml',
            u'simple.sedml',
        ], result)

    def test_note_linkage(self):
        request = TestRequest(form={
            'form.widgets.workspace': u'sedml',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]

        ExposureFileGenForm(context, TestRequest(form={
            'form.widgets.filename': [u'demo.cellml'],
            'form.buttons.add': 1,
        })).update()

        exposure_file = context[u'demo.cellml']
        loader = ExposureFileLoader()
        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        # No note, so no sedml
        self.assertEqual([
            u'demo.cellml',
        ], result)
        # Also no note is created
        self.assertFalse(has_note(exposure_file, 'opencor'))

        note = queryAdapter(exposure_file, name='opencor')
        if not note:
            raise unittest.SkipTest('no cellml.pmr available for testing')

        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        # has note. but no value, so no sedml
        self.assertTrue(has_note(exposure_file, 'opencor'))
        self.assertEqual([
            u'demo.cellml',
        ], result)

        note.filename = 'simple.sedml'

        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())
        self.assertEqual([
            u'demo.cellml',
            u'simple.sedml',
        ], result)

    def test_extract_embeded_workspace_mixed_external(self):
        # inject a modified version of the multi2 model
        su = getUtility(IStorageUtility, name='dummy_storage')
        sedml = su._dummy_storage_data['sedml']
        # hack a subrepo in there
        sedml[0]['embed'] = {
            '': '_subrepo',
            'rev': '0',
            # XXX note the lack of portal in vhost
            'location': 'http://nohost/plone/workspace/demo_model',
        }

        request = TestRequest(form={
            'form.widgets.workspace': u'sedml',
            'form.widgets.commit_id': u'0',
            'form.buttons.add': 1,
        })
        testform = ExposureAddForm(self.layer['portal'].exposure, request)
        testform.update()
        exp_id = testform._data['id']
        context = self.layer['portal'].exposure[exp_id]

        ExposureFileGenForm(context, TestRequest(form={
            'form.widgets.filename': [u'simulation.sedml'],
            'form.buttons.add': 1,
        })).update()
        ExposureFileGenForm(context, TestRequest(form={
            'form.widgets.filename': [u'demo.cellml'],
            'form.buttons.add': 1,
        })).update()

        exposure_file = context[u'simulation.sedml']
        registry = getUtility(IRegistry)
        registry['cellml.pmr2.vhost.prefix_maps'] = {u'nohost': u''}

        loader = TrackedSedMLLoader()
        urlopener = LoggedPmrUrlOpener()
        result = sorted(loader.load(exposure_file, urlopener=urlopener).keys())

        self.assertEqual([
            u'demo.cellml',
            u'embed/main/model.cellml',
            u'embed/multi.cellml',
            u'simulation.sedml',
            u'table.csv',
        ], result)
        self.assertEqual([
        ], urlopener.external)

        # also test that this full archive can be created
        archiver = ExposureGeneratedOmexArchiver()
        zipbytes = archiver.archive_exposure(context)
        zf = zipfile.ZipFile(BytesIO(zipbytes), mode='r')
        self.assertEqual(
            sorted(zf.namelist()),
            sorted(['!!autogen-disclaimer.txt', 'manifest.xml'] + result),
        )
