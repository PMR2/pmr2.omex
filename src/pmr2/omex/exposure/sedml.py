from __future__ import absolute_import

from urlparse import urlparse
from io import BytesIO
from lxml import etree

import zope.component
from zope.interface import implementer

from pmr2.app.exposure.interfaces import IExposureSourceAdapter

from cellml.pmr2.urlopener import make_pmr_path

from pmr2.omex.exposure.interfaces import IExposureFileLoader
from pmr2.omex.exposure.interfaces import DuplicateURLError
from pmr2.omex.exposure.default import ExposureFileLoader
from pmr2.omex.exposure.urlopener import LoggedPmrUrlOpener


@implementer(IExposureFileLoader)
class TrackedSedMLLoader(ExposureFileLoader):

    def process_sedml(self, sedml, exposure, workspace, urlopener):
        dom = etree.XML(sedml)
        ns = {'_': dom.nsmap[None]}
        targets = []
        targets.extend(dom.xpath('//_:model/@source', namespaces=ns))
        targets.extend(dom.xpath('//_:dataDescription/@source', namespaces=ns))

        for target in targets:
            parsed = urlparse(target)
            if parsed.scheme or parsed.netloc:
                # do not load remote resources
                continue

            # TODO maybe splitext and just have a default?
            # as a demonstration with one specific target we can get away
            # with this...
            resolved = make_pmr_path(
                '/'.join(workspace.getPhysicalPath()), exposure.commit_id,
                target,
            )

            if target.endswith('.cellml'):
                utility = zope.component.queryUtility(
                    IExposureFileLoader, name='cellml')
                if utility:
                    utility.loadTarget(resolved, urlopener=urlopener)
                    continue

            self.loadTarget(resolved, urlopener)

    def load(self, exposure_file, urlopener=None):
        urlopener = urlopener or LoggedPmrUrlOpener()
        sa = zope.component.getAdapter(exposure_file, IExposureSourceAdapter)
        # rather than processing the file directly, let the urlopener
        # track the process
        exposure, workspace, path = sa.source()
        # need this to resolve.
        root = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, '')
        urn = make_pmr_path(
            '/'.join(workspace.getPhysicalPath()), exposure.commit_id, path)

        try:
            sedml = urlopener.loadURL(urn)
        except DuplicateURLError:
            pass
        else:
            self.process_sedml(sedml, exposure, workspace, urlopener)

        return {
            key[len(root):]: value
            for key, value in urlopener.loaded.items()
            if key.startswith(root)
        }

