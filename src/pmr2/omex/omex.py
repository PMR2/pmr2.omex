from cStringIO import StringIO
from os.path import splitext
from urlparse import urlparse
from textwrap import dedent
import mimetypes
import zipfile

from lxml import etree
from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace.exceptions import StorageArchiveError
from pmr2.app.workspace.exceptions import PathNotFoundError
from pmr2.app.workspace.interfaces import IStorage


def extract_storage_manifest(storage, manifest_path='manifest.xml'):
    """
    Extract the manifest from a storage
    """

    try:
        raw_manifest = storage.file(manifest_path)
    except PathNotFoundError:
        raise ValueError
    return parse_manifest(raw_manifest)

def _fetch_pathinfo(portal, storage, path):
    """
    Assuming this is locally available.
    """

    try:
        pinfo = storage.pathinfo(path)
    except PathNotFoundError:
        raise StorageArchiveError(path)

    if pinfo.get('external'):
        parsed = urlparse(pinfo['external']['location'])
        rev = pinfo['external']['rev']
        ob = portal.restrictedTraverse(parsed.path[1:])
        storage = queryAdapter(ob, IStorage)
        if storage:
            storage.checkout(rev)
            return _fetch_pathinfo(portal, storage, pinfo['external']['path'])

    if pinfo['mimetype']():
        return path, storage.file(path)

    # can't find anything
    raise StorageArchiveError(path)

def filelist_generator(storage, paths):
    """
    Can be use a list of locations
    """
    # XXX this method will attempt to resolve subrepo targets against
    # the current portal.

    portal = getToolByName(
        storage.context, name='portal_url').getPortalObject()

    for path in paths:
        yield _fetch_pathinfo(portal, storage, path)

def build_omex(storage, manifest_path='manifest.xml'):
    """
    Build an archive from a storage backend and a path.
    """

    paths = extract_storage_manifest(storage, manifest_path)
    return _create_zip(filelist_generator(storage, paths))
    # return _process(storage.file, locations)

def _process(getter, locations):
    def generate_filemap():
        for path in locations:
            try:
                yield path, getter(path)
            except (PathNotFoundError, KeyError):
                raise StorageArchiveError(path)

    return _create_zip(generate_filemap())

def _create_zip(filemap):
    stream = StringIO()
    zf = zipfile.ZipFile(stream, mode='w')
    for path, contents in filemap:
        znfo = zipfile.ZipInfo(path)
        znfo.file_size = len(contents)
        znfo.compress_type = zipfile.ZIP_DEFLATED
        znfo.external_attr = 0o777 << 16L
        zf.writestr(znfo, contents)
    zf.close()
    return stream.getvalue()

def parse_manifest(raw_manifest):
    et = etree.parse(StringIO(raw_manifest))
    raw = et.xpath('//o:omexManifest/o:content/@location', namespaces={
        'o': 'http://identifiers.org/combine.specifications/omex-manifest'
    })
    locations = []
    for r in raw:
        if r.startswith('http://') or r.startswith('https://'):
            # ignore external resources for now
            continue
        if r == '.':
            # ignore self references.
            continue
        if r.startswith('./'):
            locations.append(r[2:])
            continue
        locations.append(r)

    # assert that 'manifest.xml' is included?
    return locations

def generate_manifest(filemap):
    identifiers_org = {
        '.cellml': "http://identifiers.org/combine.specifications/cellml",
        '.sbml': "http://identifiers.org/combine.specifications/sbml",
        '.sedml': "http://identifiers.org/combine.specifications/sedml",
        '.rdf': "http://identifiers.org/combine.specifications/omex-metadata",
    }
    omex_header = dedent('''
    <?xml version='1.0' encoding='utf-8' standalone='yes'?>
    <omexManifest
        xmlns="http://identifiers.org/combine.specifications/omex-manifest">
    ''').strip()
    omex_footer = dedent('''
    </omexManifest>
    ''').strip()
    omex_line = dedent('''
    <content location="{location}" format="{format}" />
    ''').strip()
    output = [omex_header]
    for name, content in sorted(filemap.items()):
        if name == 'manifest.xml':
            fmt = "http://identifiers.org/combine.specifications/omex-manifest"
        else:
            fext = splitext(name)[-1]
            fmt = identifiers_org.get(
                fext, "http://purl.org/NET/mediatypes/%s" % (
                    mimetypes.guess_type(name)[0]))

        output.append(omex_line.format(
            location=name,
            format=fmt,
        ))
    output.append(omex_footer)
    return '\n'.join(output)
