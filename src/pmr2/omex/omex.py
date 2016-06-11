from cStringIO import StringIO
import zipfile

from lxml import etree

from pmr2.app.workspace.exceptions import StorageArchiveError
from pmr2.app.workspace.exceptions import PathNotFoundError

def extract_storage_manifest(storage, manifest_path='manifest.xml'):
    """
    Extract the manifest from a storage
    """

    try:
        raw_manifest = storage.file(manifest_path)
    except PathNotFoundError:
        raise ValueError
    return parse_manifest(raw_manifest)

def build_omex(storage, manifest_path='manifest.xml'):
    """
    Build an archive from a storage backend and a path.
    """

    locations = extract_storage_manifest(storage, manifest_path)
    return _process(storage.file, locations)

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
