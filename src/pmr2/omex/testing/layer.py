from os.path import join, dirname

import zope.component
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.testing import z2

from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.interfaces import IStorageUtility

from pmr2.app.workspace.tests import layer


class OmexBaseLayer(PloneSandboxLayer):

    defaultBases = (layer.WORKSPACE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.omex
        self.loadZCML(package=pmr2.omex)
        z2.installProduct(app, 'pmr2.omex')

    def setUpPloneSite(self, portal):
        """
        Set up the objects required for the test layer.
        """

        # install pmr2.omex
        #self.applyProfile(portal, 'pmr2.omex:default')

        su = zope.component.getUtility(IStorageUtility, name='dummy_storage')
        su._loadDir('omex_base', join(dirname(__file__), 'omex_base'))

        w = Workspace('omex_base')
        w.storage = 'dummy_storage'
        portal.workspace['omex_base'] = w

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'pmr2.omex')


OMEX_BASE_FIXTURE = OmexBaseLayer()

OMEX_BASE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(OMEX_BASE_FIXTURE,), name="pmr2.omex:integration")


class OmexExposureLayer(PloneSandboxLayer):

    defaultBases = (OMEX_BASE_FIXTURE,)

    def setUpPloneSite(self, portal):
        """
        """

        from pmr2.app.exposure.content import ExposureContainer
        from pmr2.app.exposure.content import Exposure
        from pmr2.app.exposure.content import ExposureFile
        portal['ec'] = ExposureContainer('ec')
        portal.ec['combine_test'] = Exposure('combine_test')
        portal.ec['combine_test'].workspace = u'/plone/workspace/omex_base'
        portal.ec.combine_test['demo.xml'] = ExposureFile('demo.xml')
        portal.ec.combine_test['no_omex.xml'] = ExposureFile('no_omex.xml')


OMEX_EXPOSURE_FIXTURE = OmexExposureLayer()

OMEX_EXPOSURE_INTEGRATION_LAYER = IntegrationTesting(
    bases=(OMEX_EXPOSURE_FIXTURE,), name="pmr2.omex:exposure_integration")
