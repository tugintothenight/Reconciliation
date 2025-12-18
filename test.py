# import unittest
# from unittest.mock import MagicMock, patch
# from main import TextExtractor, TextMatcher, DiffVisualizer, DocumentComparator
#
#
# SAMPLE_DOC = [
#     "Công ty A cam kết hoàn thành dự án đúng hạn.",
#     "Tổng chi phí là 1000 USD."
# ]
# SAMPLE_PDF_EXACT = [
#     "Công ty A cam kết hoàn thành dự án đúng hạn.",
#     "Tổng chi phí là 1000 USD."
# ]
# SAMPLE_PDF_DIFF = [
#     "Công ty A cam kết hoàn thành dự án dung han.",  # Sai dấu
#     "Tổng chi phí la 2000 USD."
# ]
#
#
# class TestTextMatcher(unittest.TestCase):
#     """Kiểm tra logic so khớp (Matching Logic)"""
#
#     @classmethod
#     def setUpClass(cls):
#         cls.matcher = TextMatcher()
#
#     def test_levenshtein_exact(self):
#         """TC_01: Levenshtein khoảng cách"""
#         dist, ratio = self.matcher.levenshtein_distance("abc", "abc")
#         self.assertEqual(dist, 0)
#         self.assertEqual(ratio, 0.0)
#
#     def test_levenshtein_diff(self):
#         """TC_02: Levenshtein tính đúng số ký tự khác biệt"""
#         dist, ratio = self.matcher.levenshtein_distance("abc", "abd")
#         self.assertEqual(dist, 1)
#         self.assertAlmostEqual(ratio, 1 / 3)
#
#     def test_bm25_ranking(self):
#         """TC_03: BM25 tìm đúng câu dựa trên từ khóa"""
#         doc = ["Tôi học lập trình Python"]
#         pdf = ["Hôm nay trời đẹp", "Khóa học Python cơ bản", "Dữ liệu này không có gì"]
#         matches = self.matcher.bm25_match(doc, pdf)
#         # matches format: [(doc_idx, pdf_idx, score)]
#         matched_pdf_idx = matches[0][1]
#         self.assertEqual(matched_pdf_idx, 1)
#
#     def test_semantic_match(self):
#         """TC_04: Embedding tìm đúng ngữ nghĩa dù sai chính tả"""
#         doc = ["Xin chào thế giới"]
#         pdf = ["Goodbye world", "Xin chao the gioi"]
#         matches = self.matcher.semantic_match(doc, pdf)
#         # matches format: [(doc_idx, pdf_idx, score)]
#         matched_pdf_idx = matches[0][1]
#         score = matches[0][2]
#
#         self.assertEqual(matched_pdf_idx, 1)
#         self.assertGreater(score, 0.7)
#
#
# class TestDocumentComparator(unittest.TestCase):
#     """Kiểm tra luồng so sánh chính (Integration Test)"""
#
#     def setUp(self):
#         self.comparator = DocumentComparator()
#
#     def test_run_comparison_exact_match(self):
#         """TC_05: Chạy so sánh với dữ liệu giống hệt"""
#         results = self.comparator.run_full_comparison(
#             doc_chunks=SAMPLE_DOC,
#             pdf_chunks=SAMPLE_PDF_EXACT,
#
#         )
#         self.assertEqual(results[0]['char_distance'], 0)
#         self.assertEqual(results[0]['pdf_id_semantic'], 0)
#         self.assertEqual(results[1]['char_distance'], 0)
#
#     def test_run_comparison_with_diff(self):
#         """TC_06: Chạy so sánh với dữ liệu có sai lệch"""
#         results = self.comparator.run_full_comparison(
#             doc_chunks=SAMPLE_DOC,
#             pdf_chunks=SAMPLE_PDF_DIFF,
#         )
#
#         self.assertGreater(results[0]['char_distance'], 0)
#         self.assertGreater(results[1]['char_distance'], 0)
#
#     @patch('main.convert_from_path')
#     @patch('main.PaddleOCR')
#     def test_pdf_extraction_mock(self, mock_ocr_class, mock_convert):
#         """TC_07: Mocking OCR để test hàm extract mà không cần file PDF thật"""
#         mock_page = MagicMock()
#         mock_convert.return_value = [mock_page]
#         mock_ocr_instance = mock_ocr_class.return_value
#         # Format: [[[box], (text, score)]]
#         mock_ocr_return_data = [
#             [
#                 [[[10, 10], [20, 20]], ("Hello World", 0.99)],
#                 [[[30, 30], [40, 40]], ("Test PDF", 0.98)]
#             ]
#         ]
#         mock_ocr_instance.predict.return_value = mock_ocr_return_data
#         extractor = TextExtractor()
#         # Tạo file PDF giả (tên file thôi, không cần tồn tại vì đã mock)
#         result_text = extractor.extract_from_pdf("fake_file.pdf")
#         self.assertIn("Hello World", result_text)
#
#
# if __name__ == '__main__':
#     unittest.main()