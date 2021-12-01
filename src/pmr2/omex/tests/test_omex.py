from unittest import TestCase, TestSuite, makeSuite

from pmr2.omex.omex import (
    parse_manifest,
    generate_manifest,
)

demo_omex = '''<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<omexManifest
    xmlns="http://identifiers.org/combine.specifications/omex-manifest">
  <content location="./manifest.xml"
    format="http://identifiers.org/combine.specifications/omex-manifest" />
  <content location="./BorisEJB.xml"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./paper/Kholodenko2000.pdf"
    format="http://purl.org/NET/mediatypes/application/pdf" />
  <content location="http://www.ebi.ac.uk/biomodels-main/BIOMD0000000010"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./metadata.rdf"
    format="http://identifiers.org/combine.specifications/omex-metadata" />
</omexManifest>'''

with_dot_omex = '''<?xml version='1.0' encoding='utf-8' standalone='yes'?>
<omexManifest
    xmlns="http://identifiers.org/combine.specifications/omex-manifest">
  <content location="."
    format="http://identifiers.org/combine.specifications/omex" />
  <content location="./manifest.xml"
    format="http://identifiers.org/combine.specifications/omex-manifest" />
  <content location="./BorisEJB.xml"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./paper/Kholodenko2000.pdf"
    format="http://purl.org/NET/mediatypes/application/pdf" />
  <content location="http://www.ebi.ac.uk/biomodels-main/BIOMD0000000010"
    format="http://identifiers.org/combine.specifications/sbml" />
  <content location="./metadata.rdf"
    format="http://identifiers.org/combine.specifications/omex-metadata" />
</omexManifest>'''


class TestOmex(TestCase):
    """
    Test Omex Core.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_manifest_load(self):
        results = parse_manifest(demo_omex)
        self.assertEqual(results,
            ['manifest.xml', 'BorisEJB.xml', 'paper/Kholodenko2000.pdf',
            'metadata.rdf'])

    def test_manifest_load_with_dot(self):
        results = parse_manifest(demo_omex)
        self.assertEqual(results,
            ['manifest.xml', 'BorisEJB.xml', 'paper/Kholodenko2000.pdf',
            'metadata.rdf'])

    def test_generate_manifest(self):
        manifest = generate_manifest({
            '.': '',
            'demo1.cellml': '',
            'demo1.sedml': '',
            'manifest.xml': '',
            'metadata.rdf': '',
            'image.png': '',
        })
        results = parse_manifest(manifest)
        self.assertEqual(results, [
            'demo1.cellml',
            'demo1.sedml',
            'image.png',
            'manifest.xml',
            'metadata.rdf',
        ])
        # just check that these are present int he output.
        self.assertIn(
            '<content location="." '
            'format="http://identifiers.org/combine.specifications/omex" />',
            manifest,
        )
        self.assertIn(
            "http://identifiers.org/combine.specifications/cellml",
            manifest,
        )
        self.assertIn(
            "http://identifiers.org/combine.specifications/omex-metadata",
            manifest,
        )
        self.assertIn(
            "http://purl.org/NET/mediatypes/image/png",
            manifest,
        )

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOmex))
    return suite

