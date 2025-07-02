import unittest
from unittest.mock import patch, Mock
from ..modules.api_manager import fetch_book_data_google
import requests # Import requests for exception testing

class TestApiManager(unittest.TestCase):

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_success(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "totalItems": 1,
            "items": [
                {
                    "volumeInfo": {
                        "title": "Test Book",
                        "authors": ["Test Author"]
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        isbn = "9781234567890"
        data = fetch_book_data_google(isbn, api_key="fake_key")

        self.assertIsNotNone(data)
        self.assertEqual(data["volumeInfo"]["title"], "Test Book")
        mock_get.assert_called_once_with(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f"isbn:{isbn}", "key": "fake_key"},
            timeout=10
        )

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_no_items(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"totalItems": 0, "items": []}
        mock_get.return_value = mock_response

        data = fetch_book_data_google("0000000000")
        self.assertIsNone(data)

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        # Add text attribute for error logging in api_manager
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        data = fetch_book_data_google("1234567890")
        self.assertIsNone(data)
        # Check that raise_for_status was called, which implies an HTTPError was handled
        mock_response.raise_for_status.assert_called_once()


    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        data = fetch_book_data_google("1234567890")
        self.assertIsNone(data)

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        data = fetch_book_data_google("1234567890")
        self.assertIsNone(data)

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_json_decode_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Error decoding JSON", "doc", 0)
        # Some versions of requests library might raise json.JSONDecodeError directly
        # from json import JSONDecodeError
        # mock_response.json.side_effect = JSONDecodeError("Error decoding JSON", "doc", 0)

        mock_get.return_value = mock_response

        data = fetch_book_data_google("1234567890")
        self.assertIsNone(data)

    @patch('isbn_bibliographer.modules.api_manager.requests.get')
    def test_fetch_book_data_google_no_api_key(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "totalItems": 1,
            "items": [{"volumeInfo": {"title": "No Key Book"}}]
        }
        mock_get.return_value = mock_response

        isbn = "9780987654321"
        data = fetch_book_data_google(isbn) # API key not provided

        self.assertIsNotNone(data)
        self.assertEqual(data["volumeInfo"]["title"], "No Key Book")
        mock_get.assert_called_once_with(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f"isbn:{isbn}"}, # No 'key' in params
            timeout=10
        )

if __name__ == '__main__':
    unittest.main()
