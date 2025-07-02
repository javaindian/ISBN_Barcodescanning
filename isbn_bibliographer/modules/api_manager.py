import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# In a real application, API_KEY would be loaded from a config file or environment variable
API_KEY = None # Replace with your actual Google Books API key if you have one

def fetch_book_data_google(isbn: str, api_key: str = None) -> dict | None:
    """
    Fetches book data from the Google Books API using an ISBN.

    Args:
        isbn (str): The ISBN (10 or 13) of the book.
        api_key (str, optional): Google Books API key. Defaults to None.

    Returns:
        dict | None: A dictionary containing book information if found, else None.
    """
    params = {
        "q": f"isbn:{isbn}"
    }
    if api_key:
        params["key"] = api_key

    try:
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params, timeout=10) # 10 seconds timeout
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        data = response.json()

        if data.get("totalItems", 0) > 0 and data.get("items"):
            # Typically, the first item is the most relevant for a specific ISBN query
            book_info = data["items"][0]
            return book_info
        else:
            logging.warning(f"No items found for ISBN {isbn} in Google Books API response.")
            return None

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while fetching data for ISBN {isbn}: {http_err} - {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred while fetching data for ISBN {isbn}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred while fetching data for ISBN {isbn}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An unexpected error occurred while fetching data for ISBN {isbn}: {req_err}")
    except json.JSONDecodeError:
        logging.error(f"Failed to decode JSON response for ISBN {isbn}.")

    return None

if __name__ == '__main__':
    # Test cases
    # Note: To run these tests effectively, you might need a valid Google Books API key.
    # Without an API key, requests are subject to lower quotas and might be less reliable.

    # You can set your API_KEY here for testing, or pass it directly
    # test_api_key = "YOUR_GOOGLE_BOOKS_API_KEY"
    test_api_key = API_KEY # Uses the global API_KEY which is None by default

    sample_isbn13 = "9780306406157" # A known valid ISBN-13
    sample_isbn10 = "0306406152"   # A known valid ISBN-10
    invalid_isbn = "1234567890"     # An invalid ISBN
    non_existent_isbn = "9780000000000" # A structurally valid but likely non-existent ISBN

    print(f"--- Testing with API Key: {'Provided' if test_api_key else 'Not Provided'} ---")

    print(f"\nFetching data for ISBN-13: {sample_isbn13}")
    book_data_13 = fetch_book_data_google(sample_isbn13, api_key=test_api_key)
    if book_data_13:
        print(f"Title: {book_data_13.get('volumeInfo', {}).get('title')}")
        # print(json.dumps(book_data_13, indent=2)) # Uncomment to see full response
    else:
        print("No data found or error occurred.")

    time.sleep(1) # Simple delay to avoid hitting rate limits if any

    print(f"\nFetching data for ISBN-10: {sample_isbn10}")
    book_data_10 = fetch_book_data_google(sample_isbn10, api_key=test_api_key)
    if book_data_10:
        print(f"Title: {book_data_10.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred.")

    time.sleep(1)

    print(f"\nFetching data for invalid ISBN structure: {invalid_isbn}")
    # The API might not error on "invalid" ISBNs if they are just numbers,
    # it will simply not find them. Validation should happen before calling the API.
    book_data_invalid = fetch_book_data_google(invalid_isbn, api_key=test_api_key)
    if book_data_invalid:
        print(f"Title: {book_data_invalid.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred (as expected for invalid/non-existent ISBN).")

    time.sleep(1)

    print(f"\nFetching data for non-existent ISBN: {non_existent_isbn}")
    book_data_non_existent = fetch_book_data_google(non_existent_isbn, api_key=test_api_key)
    if book_data_non_existent:
        print(f"Title: {book_data_non_existent.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred (as expected for non-existent ISBN).")

    # Example of how it might be used with an API key from a config file (conceptual)
    # try:
    #     with open("config.json", "r") as f:
    #         config = json.load(f)
    #         API_KEY_FROM_CONFIG = config.get("google_books_api_key")
    # except FileNotFoundError:
    #     API_KEY_FROM_CONFIG = None
    #
    # if API_KEY_FROM_CONFIG:
    #     print("\n--- Testing with API Key from hypothetical config.json ---")
    #     book_data_config_key = fetch_book_data_google(sample_isbn13, api_key=API_KEY_FROM_CONFIG)
    #     if book_data_config_key:
    #         print(f"Title: {book_data_config_key.get('volumeInfo', {}).get('title')}")
    #     else:
    #         print("No data found or error occurred.")
    # else:
    #     print("\nSkipping test with config file API key (config.json or key not found).")
