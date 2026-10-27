import re
import unittest
from unittest.mock import patch
import extractor


class ExtractionTests(unittest.TestCase):
    def test_portuguese_thousands_and_decimals(self):
        text = 'N 7.654.321,23 E 500.123,45'
        with patch.object(extractor, 'extract_text_from_pdf', return_value=text):
            points, _, _ = extractor.extrair_vertices('unused')
        self.assertEqual(points, [(500123.45, 7654321.23)])

    def test_header_matches_whole_words(self):
        header = ['VÉRTICE', 'NORTE', 'ESTE']
        self.assertEqual(extractor._find_column_index(header, extractor.EASTING_HEADER_CANDIDATES), 2)
        self.assertEqual(extractor._find_column_index(header, extractor.VERTEX_HEADER_CANDIDATES), 0)

    def test_generic_range_rejects_unrealistic_easting(self):
        self.assertIsNone(extractor._classify_by_magnitude(7654321, 42))
        self.assertEqual(extractor._classify_by_magnitude(7654321, 500000), (7654321, 500000))

    def test_auto_detects_formatted_pairs(self):
        text = ' '.join('N 7.654.32%d,23 E 500.12%d,45' % (i, i) for i in range(3))
        with patch.object(extractor, '_extract_from_tables', return_value=[]), patch.object(extractor, 'extract_text_from_pdf', return_value=text):
            result = extractor.auto_extract_vertices('unused')
        self.assertEqual(len(result['pontos']), 3)
        self.assertEqual(result['pontos'][0], (500120.45, 7654320.23))

if __name__ == '__main__':
    unittest.main()
