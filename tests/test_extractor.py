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

class PreservationTests(unittest.TestCase):
    def test_consecutive_duplicates_preserved_in_both_modes(self):
        text = 'N 7491240.70 E 206585.00 N 7491240.70 E 206585.00 N 7491567.58 E 206099.95'
        with patch.object(extractor, 'extract_text_from_pdf', return_value=text), patch.object(extractor, '_extract_from_tables', return_value=[]):
            manual, _, _ = extractor.extrair_vertices('unused')
            auto = extractor.auto_extract_vertices('unused')['pontos']
        self.assertEqual(len(manual), 3)
        self.assertEqual(auto, manual)
        self.assertEqual(auto[0], auto[1])

    def test_labels_are_not_swapped_by_magnitude(self):
        text = 'N 200000 E 7000000 N 200001 E 7000001 N 200002 E 7000002'
        with patch.object(extractor, 'extract_text_from_pdf', return_value=text), patch.object(extractor, '_extract_from_tables', return_value=[]):
            result = extractor.auto_extract_vertices('unused')
        self.assertEqual(result['pontos'][0], (7000000, 200000))

    def test_table_columns_are_not_swapped_by_magnitude(self):
        rows = [(200000, 7000000, 'Pt1'), (200001, 7000001, 'Pt2'), (200002, 7000002, 'Pt3')]
        with patch.object(extractor, '_extract_from_tables', return_value=rows):
            result = extractor.auto_extract_vertices('unused')
        self.assertEqual(result['pontos'][0], (7000000, 200000))

class ClosingVertexTests(unittest.TestCase):
    def _extract(self, text):
        with patch.object(extractor, 'extract_text_from_pdf', return_value=text), patch.object(extractor, '_extract_from_tables', return_value=[]):
            return extractor.extrair_vertices('unused')[0], extractor.auto_extract_vertices('unused')['pontos']

    def test_explicit_same_vertex_at_end_is_omitted(self):
        text = ('vértice Pt0, de coordenadas N 7490000.00 E 200000.00; '
                'vértice Pt1, de coordenadas N 7491000 E 200001; '
                'vértice Pt0, de coordenadas N 7490000 E 200000')
        for points in self._extract(text):
            self.assertEqual(points, [(200000, 7490000), (200001, 7491000)])

    def test_distinct_vertex_with_same_coordinates_is_preserved(self):
        text = ('vértice Pt0, de coordenadas N 7490000 E 200000; '
                'vértice Pt1, de coordenadas N 7491000 E 200001; '
                'vértice Pt2, de coordenadas N 7490000 E 200000')
        for points in self._extract(text):
            self.assertEqual(len(points), 3)
            self.assertEqual(points[0], points[-1])

    def test_different_coordinates_before_rounding_are_preserved(self):
        rows = [(7490000.001, 200000, 'Pt0'), (7491000, 200001, 'Pt1'), (7492000, 200002, 'Pt2'), (7490000.002, 200000, 'Pt0')]
        with patch.object(extractor, '_extract_from_tables', return_value=rows):
            self.assertEqual(len(extractor.auto_extract_vertices('unused')['pontos']), 4)

    def test_table_explicit_closing_vertex(self):
        rows = [(7490000, 200000, 'Pt0'), (7491000, 200001, 'Pt1'), (7492000, 200002, 'Pt2'), (7490000, 200000, 'Pt0')]
        with patch.object(extractor, '_extract_from_tables', return_value=rows):
            self.assertEqual(len(extractor.auto_extract_vertices('unused')['pontos']), 3)
