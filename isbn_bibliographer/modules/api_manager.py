import requests
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

# API_KEY is no longer used directly here as calls will be unauthenticated.

def fetch_book_data_google(isbn: str) -> dict | None:
    """
    Fetches book data from the Google Books API using an ISBN via unauthenticated requests.

    Args:
        isbn (str): The ISBN (10 or 13) of the book.

    Returns:
        dict | None: A dictionary containing book information if found, else None.
    """
    params = {
        "q": f"isbn:{isbn}"
    }
    # No API key is added to params for unauthenticated requests

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
    # Note: API calls are now unauthenticated.

    sample_isbn13 = "9780306406157" # A known valid ISBN-13
    sample_isbn10 = "0306406152"   # A known valid ISBN-10
    invalid_isbn = "1234567890"     # An invalid ISBN
    non_existent_isbn = "9780000000000" # A structurally valid but likely non-existent ISBN

    print(f"--- Testing Google Books API (Unauthenticated) ---")

    print(f"\nFetching data for ISBN-13: {sample_isbn13}")
    book_data_13 = fetch_book_data_google(sample_isbn13) # No api_key argument
    if book_data_13:
        print(f"Title: {book_data_13.get('volumeInfo', {}).get('title')}")
        # print(json.dumps(book_data_13, indent=2)) # Uncomment to see full response
    else:
        print("No data found or error occurred.")

    time.sleep(1) # Simple delay to avoid hitting rate limits if any

    print(f"\nFetching data for ISBN-10: {sample_isbn10}")
    book_data_10 = fetch_book_data_google(sample_isbn10) # No api_key argument
    if book_data_10:
        print(f"Title: {book_data_10.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred.")

    time.sleep(1)

    print(f"\nFetching data for invalid ISBN structure: {invalid_isbn}")
    # The API might not error on "invalid" ISBNs if they are just numbers,
    # it will simply not find them. Validation should happen before calling the API.
    book_data_invalid = fetch_book_data_google(invalid_isbn) # No api_key argument
    if book_data_invalid:
        print(f"Title: {book_data_invalid.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred (as expected for invalid/non-existent ISBN).")

    time.sleep(1)

    print(f"\nFetching data for non-existent ISBN: {non_existent_isbn}")
    book_data_non_existent = fetch_book_data_google(non_existent_isbn) # No api_key argument
    if book_data_non_existent:
        print(f"Title: {book_data_non_existent.get('volumeInfo', {}).get('title')}")
    else:
        print("No data found or error occurred (as expected for non-existent ISBN).")

    # The conceptual test for API key from config is no longer relevant here.
