import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_book_data(api_response: Dict[str, Any], source_api: str = "google") -> Dict[str, Any]:
    """
    Formats book data from an API response into a structured bibliography dictionary.
    Currently tailored for Google Books API response structure.

    Args:
        api_response (Dict[str, Any]): The raw API response for a single book.
        source_api (str): Identifier for the source API (e.g., "google", "openlibrary").
                          This helps in adapting parsing logic if multiple sources are used.

    Returns:
        Dict[str, Any]: A dictionary containing formatted book information.
                        Returns a minimal dictionary with an error if formatting fails.
    """
    formatted_data: Dict[str, Any] = {
        "Input ISBN": None, # Will be populated by the main script
        "Title": None,
        "Subtitle": None,
        "Authors": None, # List of strings
        "Publisher": None,
        "Publication Date": None, # YYYY-MM-DD or YYYY-MM or YYYY
        "Publication Year": None, # Extracted YYYY
        "ISBN-10": None,
        "ISBN-13": None,
        "Page Count": None,
        "Language": None, # ISO 639-1 code e.g. "en"
        "Edition": None,
        "Description": None,
        "Categories": None, # List of strings
        "Cover Image URL": None,
        "Source API": source_api,
        "Error": None
    }

    if not api_response or not isinstance(api_response, dict):
        logging.warning("format_book_data received empty or invalid api_response.")
        formatted_data["Error"] = "Invalid API response received for formatting."
        return formatted_data

    try:
        if source_api.lower() == "google":
            volume_info = api_response.get("volumeInfo", {})
            if not volume_info:
                formatted_data["Error"] = "API response missing 'volumeInfo'."
                return formatted_data

            formatted_data["Title"] = volume_info.get("title")
            formatted_data["Subtitle"] = volume_info.get("subtitle")

            authors = volume_info.get("authors")
            if authors and isinstance(authors, list):
                formatted_data["Authors"] = ", ".join(authors) # Store as comma-separated string for now

            formatted_data["Publisher"] = volume_info.get("publisher")

            published_date_raw = volume_info.get("publishedDate")
            formatted_data["Publication Date"] = published_date_raw
            if published_date_raw and isinstance(published_date_raw, str):
                # Extract year. Handles YYYY, YYYY-MM, YYYY-MM-DD
                year_match = published_date_raw.split('-')[0]
                if year_match.isdigit() and len(year_match) == 4:
                    formatted_data["Publication Year"] = year_match

            industry_identifiers = volume_info.get("industryIdentifiers", [])
            for identifier in industry_identifiers:
                if identifier.get("type") == "ISBN_10":
                    formatted_data["ISBN-10"] = identifier.get("identifier")
                elif identifier.get("type") == "ISBN_13":
                    formatted_data["ISBN-13"] = identifier.get("identifier")

            formatted_data["Page Count"] = volume_info.get("pageCount")
            formatted_data["Language"] = volume_info.get("language") # e.g., "en"
            # Google Books API doesn't typically provide "Edition" directly in a standard field.
            # It might sometimes be in the title or description.

            formatted_data["Description"] = volume_info.get("description")

            categories = volume_info.get("categories")
            if categories and isinstance(categories, list):
                formatted_data["Categories"] = ", ".join(categories) # Store as comma-separated string

            image_links = volume_info.get("imageLinks", {})
            formatted_data["Cover Image URL"] = image_links.get("thumbnail") or image_links.get("smallThumbnail")

        # Add parsers for other APIs here using elif source_api.lower() == "other_api_name":
        # elif source_api.lower() == "openlibrary":
            # ... parsing logic for Open Library ...
            # pass

        else:
            formatted_data["Error"] = f"Unsupported source API: {source_api}"
            logging.warning(f"No formatting logic implemented for source API: {source_api}")

    except Exception as e:
        logging.error(f"Error formatting book data from {source_api}: {e}. API Response: {str(api_response)[:500]}...") # Log part of response
        formatted_data["Error"] = f"Exception during data formatting: {str(e)}"

    return formatted_data


if __name__ == '__main__':
    print("--- Testing Bibliography Formatter ---")

    # Sample Google Books API response (simplified)
    sample_google_response_full = {
        "kind": "books#volume",
        "id": "tZ4VvQAACAAJ",
        "etag": "someETag",
        "selfLink": "someLink",
        "volumeInfo": {
            "title": "The Hitchhiker's Guide to the Galaxy",
            "authors": ["Douglas Adams"],
            "publisher": "Pan Macmillan",
            "publishedDate": "2009-09-01",
            "description": "Seconds before the Earth is demolished to make way for a galactic freeway...",
            "industryIdentifiers": [
                {"type": "ISBN_10", "identifier": "0330508539"},
                {"type": "ISBN_13", "identifier": "9780330508537"}
            ],
            "pageCount": 224,
            "categories": ["Science fiction", "Humor"],
            "imageLinks": {
                "smallThumbnail": "http://books.google.com/books/content?id=tZ4VvQAACAAJ&printsec=frontcover&img=1&zoom=5&source=gbs_api",
                "thumbnail": "http://books.google.com/books/content?id=tZ4VvQAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"
            },
            "language": "en",
            "previewLink": "somePreviewLink",
            "infoLink": "someInfoLink",
            "canonicalVolumeLink": "someCanonicalLink"
        },
        "saleInfo": {"country": "US", "saleability": "NOT_FOR_SALE", "isEbook": False},
        "accessInfo": {"country": "US", "viewability": "NO_PAGES", "epub": {"isAvailable": False}, "pdf": {"isAvailable": False}}
    }

    sample_google_response_minimal = {
        "volumeInfo": {
            "title": "Another Book",
            "publishedDate": "2021", # Only year
             "industryIdentifiers": [
                {"type": "ISBN_13", "identifier": "9781234567890"}
            ]
        }
    }

    sample_google_response_missing_volumeinfo = {
        "kind": "books#volumes", # e.g. if the item itself was not found correctly
        "totalItems": 0
    }

    sample_google_response_empty = {}

    print("\n--- Test Case 1: Full Google Books API Response ---")
    formatted1 = format_book_data(sample_google_response_full, source_api="google")
    # print(json.dumps(formatted1, indent=2)) # For detailed view
    assert formatted1["Title"] == "The Hitchhiker's Guide to the Galaxy"
    assert formatted1["Authors"] == "Douglas Adams"
    assert formatted1["Publisher"] == "Pan Macmillan"
    assert formatted1["Publication Date"] == "2009-09-01"
    assert formatted1["Publication Year"] == "2009"
    assert formatted1["ISBN-10"] == "0330508539"
    assert formatted1["ISBN-13"] == "9780330508537"
    assert formatted1["Page Count"] == 224
    assert formatted1["Language"] == "en"
    assert "galactic freeway" in formatted1["Description"]
    assert formatted1["Categories"] == "Science fiction, Humor"
    assert formatted1["Cover Image URL"] is not None
    assert formatted1["Error"] is None
    print("Test Case 1 Passed.")

    print("\n--- Test Case 2: Minimal Google Books API Response ---")
    formatted2 = format_book_data(sample_google_response_minimal, source_api="google")
    assert formatted2["Title"] == "Another Book"
    assert formatted2["Authors"] is None # Not provided in minimal sample
    assert formatted2["Publication Year"] == "2021"
    assert formatted2["ISBN-13"] == "9781234567890"
    assert formatted2["Error"] is None
    print("Test Case 2 Passed.")

    print("\n--- Test Case 3: API Response Missing 'volumeInfo' ---")
    formatted3 = format_book_data(sample_google_response_missing_volumeinfo, source_api="google")
    assert formatted3["Error"] == "API response missing 'volumeInfo'."
    assert formatted3["Title"] is None
    print("Test Case 3 Passed.")

    print("\n--- Test Case 4: Empty API Response ---")
    formatted4 = format_book_data(sample_google_response_empty, source_api="google")
    assert formatted4["Error"] == "API response missing 'volumeInfo'." # volumeInfo is checked first
    print("Test Case 4 Passed.")

    print("\n--- Test Case 5: Invalid API Response (None) ---")
    formatted5 = format_book_data(None, source_api="google")
    assert formatted5["Error"] == "Invalid API response received for formatting."
    print("Test Case 5 Passed.")

    print("\n--- Test Case 6: Unsupported API Source ---")
    formatted6 = format_book_data(sample_google_response_full, source_api="new_api")
    assert formatted6["Error"] == "Unsupported source API: new_api"
    assert formatted6["Title"] is None # Should not have parsed Google fields
    print("Test Case 6 Passed.")

    # Example of a date with only year and month
    sample_google_response_ym_date = {
        "volumeInfo": {
            "title": "Book with YM Date",
            "publishedDate": "2023-07"
        }
    }
    print("\n--- Test Case 7: Google Books API Response with YYYY-MM Date ---")
    formatted7 = format_book_data(sample_google_response_ym_date, source_api="google")
    assert formatted7["Publication Date"] == "2023-07"
    assert formatted7["Publication Year"] == "2023"
    assert formatted7["Error"] is None
    print("Test Case 7 Passed.")

    print("\nAll formatter tests completed.")
