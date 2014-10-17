from os.path import join, dirname

import zope.component
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.testing import z2

from pmr2.app.workspace.tests import layer
from pmr2.app.workspace.content import Workspace
from pmr2.app.workspace.interfaces import IStorageUtility


class OmexBaseLayer(PloneSandboxLayer):

    defaultBases = (layer.WORKSPACE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import pmr2.omex
        self.loadZCML(package=pmr2.omex)
        z2.installProduct(app, 'pmr2.omex')

    def setUpPloneSite(self, portal):
        """
        Apply the default pmr2.omex profile and ensure that the settings
        have the tmpdir applied in.
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
