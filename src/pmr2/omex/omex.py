from cStringIO import StringIO
from itertools import chain
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


def get_storage_manifest(storage, manifest_path='manifest.xml'):
    """
    Extract the manifest from a storage
    """

    try:
        raw_manifest = storage.file(manifest_path)
    except PathNotFoundError:
        raise ValueError
    return raw_manifest

def extract_storage_manifest(storage, manifest_path='manifest.xml'):
    """
    Extract the manifest from a storage
    """

    return parse_manifest(get_storage_manifest(manifest_path))

def _fetch_pathinfo(portal, storage, path, root=''):
    """
    Assuming this is locally available.
    """

    storage_path = '/'.join((root, path)) if root else path
    try:
        pinfo = storage.pathinfo(storage_path)
    except PathNotFoundError:
        raise StorageArchiveError(storage_path)

    if pinfo.get('external'):
        parsed = urlparse(pinfo['external']['location'])
        rev = pinfo['external']['rev']
        ob = portal.restrictedTraverse(parsed.path[1:])
        storage = queryAdapter(ob, IStorage)
        if storage:
            storage.checkout(rev)
            return _fetch_pathinfo(portal, storage, pinfo['external']['path'])

    if pinfo['mimetype']():
        return path, storage.file(storage_path)

    # can't find anything
    raise StorageArchiveError(storage_path)

def filelist_generator(storage, paths, root=''):
    """
    Can be use a list of locations
    """
    # XXX this method will attempt to resolve subrepo targets against
    # the current portal.

    portal = getToolByName(
        storage.context, name='portal_url').getPortalObject()

    for path in paths:
        yield _fetch_pathinfo(portal, storage, path, root)

def build_omex(storage, manifest_path='manifest.xml'):
    """
    Build an archive from a storage backend and a path.
    """

    manifest = get_storage_manifest(storage, manifest_path)
    paths = parse_manifest(manifest)
    frags = manifest_path.rsplit('/')
    root = frags[0] if len(frags) > 1 else ''
    entries = filelist_generator(storage, paths, root)
    if 'manifest.xml' not in paths:
        # inject the incoming manifest.xml as the manifest
        entries = chain(
            entries,
            (('manifest.xml', manifest,),)
        )
    return _create_zip(entries)
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
        if path == '.':
            continue
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
        if name == '.':
            fmt = "http://identifiers.org/combine.specifications/omex"
        elif name == 'manifest.xml':
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
