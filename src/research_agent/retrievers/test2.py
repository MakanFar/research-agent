import unittest
from unittest.mock import patch
from semantic_scholar import SemanticScholarSearch  # Update the import path if needed


class TestSemanticScholarSearch(unittest.TestCase):

    @patch("semantic_scholar.requests.get")  # Mock the requests.get call
    def test_successful_search(self, mock_get):
        # Mock API response data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [
                {
                    "title": "Test Paper",
                    "abstract": "This is a test abstract.",
                    "url": "http://testurl.com",
                    "venue": "Test Conference",
                    "year": 2023,
                    "authors": [{"name": "Author A"}],
                    "isOpenAccess": True,
                    "openAccessPdf": {"url": "http://pdfurl.com"}
                }
            ]
        }

        searcher = SemanticScholarSearch("test query")
        results = searcher.search(max_results=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Paper")
        self.assertEqual(results[0]["href"], "http://pdfurl.com")
        self.assertEqual(results[0]["body"], "This is a test abstract.")

    @patch("semantic_scholar.requests.get")
    def test_api_failure(self, mock_get):
        # Simulate a network error
        mock_get.side_effect = Exception("Network failure")

        searcher = SemanticScholarSearch("test query")
        results = searcher.search(max_results=5)

        self.assertEqual(results, [])

    def test_invalid_sort_criterion(self):
        with self.assertRaises(AssertionError) as context:
            SemanticScholarSearch("test query", sort="invalidSort")

        self.assertIn("Invalid sort criterion", str(context.exception))


if __name__ == "__main__":
    unittest.main()
