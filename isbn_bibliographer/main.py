# Main script for the ISBN Bibliographer application
import argparse
import logging
import time
import json # Added for loading config if used later

from modules.isbn_validator import normalize_isbn, is_valid_isbn10, is_valid_isbn13, to_isbn13
from modules.api_manager import fetch_book_data_google
from modules.excel_processor import read_isbns_from_excel, write_bibliography_to_excel
from modules.bibliography_formatter import format_book_data

# Configure logging for the main script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [MAIN] - %(message)s')

# --- Configuration Loading (Placeholder for Step 9) ---
# This section will be enhanced in a later step to load from a config file.
CONFIG = {
    "google_books_api_key": None, # User should replace this or use a config file
    "isbn_column_name": "ISBN",
    "output_sheet_name": "Bibliography",
    "api_source_priority": ["google"], # For future expansion with multiple APIs
    "rate_limit_delay": 1 # Seconds to wait between API calls (basic rate limiting)
}

def load_config(config_path: str = None) -> None:
    """Loads configuration from a JSON file, updating the global CONFIG."""
    global CONFIG
    if config_path:
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            CONFIG.update(user_config)
            logging.info(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            logging.warning(f"Configuration file {config_path} not found. Using default/hardcoded config.")
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {config_path}. Using default/hardcoded config.")
        except Exception as e:
            logging.error(f"Error loading config {config_path}: {e}. Using default/hardcoded config.")
    else:
        logging.info("No config file specified. Using default/hardcoded config.")
    # Ensure essential keys have default values if not in user_config or no config file
    CONFIG.setdefault("google_books_api_key", None)
    CONFIG.setdefault("isbn_column_name", "ISBN")
    CONFIG.setdefault("output_sheet_name", "Bibliography")
    CONFIG.setdefault("api_source_priority", ["google"])
    CONFIG.setdefault("rate_limit_delay", 1)


def process_single_isbn(isbn_raw: str, api_key: str = None, preferred_api: str = "google"):
    """
    Processes a single raw ISBN string: normalize, validate, fetch data, format.
    """
    normalized_isbn = normalize_isbn(isbn_raw)
    logging.info(f"Processing ISBN: {isbn_raw} (Normalized: {normalized_isbn})")

    # Validate and determine type
    valid_isbn10 = is_valid_isbn10(normalized_isbn)
    valid_isbn13 = is_valid_isbn13(normalized_isbn)

    isbn_to_query = None
    query_type = None

    if valid_isbn13:
        isbn_to_query = normalized_isbn
        query_type = "ISBN-13"
    elif valid_isbn10:
        isbn_to_query = normalized_isbn # Google API handles ISBN-10
        # isbn_to_query = to_isbn13(normalized_isbn) # Or convert to ISBN-13 first
        # if not isbn_to_query:
        #     logging.error(f"Failed to convert valid ISBN-10 {normalized_isbn} to ISBN-13.")
        #     return {"Input ISBN": isbn_raw, "Error": "ISBN-10 to ISBN-13 conversion failed"}
        query_type = "ISBN-10"
    else:
        logging.warning(f"Invalid ISBN format: {isbn_raw} (Normalized: {normalized_isbn})")
        return {"Input ISBN": isbn_raw, "Error": "Invalid ISBN format"}

    logging.info(f"Querying API for {query_type}: {isbn_to_query}")

    book_api_response = None
    api_source_used = None

    # Simple API selection, will be expanded for multiple sources and fallback
    if preferred_api.lower() == "google":
        book_api_response = fetch_book_data_google(isbn_to_query, api_key=api_key)
        api_source_used = "google"
    # Add other APIs here with elif preferred_api.lower() == "openlibrary": etc.

    if book_api_response:
        formatted_book_data = format_book_data(book_api_response, source_api=api_source_used)
        formatted_book_data["Input ISBN"] = isbn_raw # Add original ISBN to the output
        if not formatted_book_data.get("ISBN-10") and not formatted_book_data.get("ISBN-13"):
             # If API didn't return ISBNs, fill from validated input
            if valid_isbn10: formatted_book_data["ISBN-10"] = normalized_isbn
            if valid_isbn13: formatted_book_data["ISBN-13"] = normalized_isbn
            if valid_isbn10 and not valid_isbn13: # if original was ISBN-10, make sure ISBN-13 is also there if possible
                converted_isbn13 = to_isbn13(normalized_isbn)
                if converted_isbn13: formatted_book_data["ISBN-13"] = converted_isbn13

        logging.info(f"Successfully fetched and formatted data for ISBN: {isbn_raw}")
        return formatted_book_data
    else:
        logging.warning(f"No data found by API for ISBN: {isbn_raw} (Query: {isbn_to_query})")
        return {"Input ISBN": isbn_raw, "Error": f"No data found by {api_source_used} API for {query_type} {isbn_to_query}"}


def main():
    parser = argparse.ArgumentParser(description="ISBN Bibliographer: Process ISBNs from Excel and retrieve book information.")
    parser.add_argument("input_excel", help="Path to the input Excel file (.xlsx, .xls) containing ISBNs.")
    parser.add_argument("output_excel", help="Path for the output Excel file (.xlsx) with bibliography data.")
    parser.add_argument("--config", help="Path to a JSON configuration file.", default=None)
    # Add more arguments as needed: --api, --scanner-mode, etc.
    # For now, focusing on core batch processing.
    # parser.add_argument("--isbn_column", help="Name of the column containing ISBNs in the input file.", default="ISBN") # Will use from CONFIG
    # parser.add_argument("--sheet_name", help="Name of the sheet for the output Excel file.", default="Bibliography") # Will use from CONFIG

    args = parser.parse_args()

    load_config(args.config) # Load config if provided

    logging.info(f"Starting ISBN Bibliography process...")
    logging.info(f"Input file: {args.input_excel}")
    logging.info(f"Output file: {args.output_excel}")
    logging.info(f"Using ISBN column: {CONFIG['isbn_column_name']}")

    raw_isbns = read_isbns_from_excel(args.input_excel, isbn_column_name=CONFIG["isbn_column_name"])

    if not raw_isbns:
        logging.warning("No ISBNs found in the input file or an error occurred during reading.")
        # Create an empty output file or one with just headers?
        # For now, just exit if no ISBNs.
        print("No ISBNs to process. Exiting.")
        return

    bibliography_data = []
    total_isbns = len(raw_isbns)
    processed_count = 0
    success_count = 0
    failure_count = 0

    for isbn_raw in raw_isbns:
        processed_count += 1
        logging.info(f"Processing ISBN {processed_count}/{total_isbns}: {isbn_raw}")

        # Basic rate limiting
        if processed_count > 1 and CONFIG["rate_limit_delay"] > 0:
            logging.debug(f"Waiting for {CONFIG['rate_limit_delay']}s before next API call...")
            time.sleep(CONFIG["rate_limit_delay"])

        # For now, only Google API is implemented
        api_to_use = CONFIG["api_source_priority"][0] if CONFIG["api_source_priority"] else "google"

        result = process_single_isbn(isbn_raw, api_key=CONFIG["google_books_api_key"], preferred_api=api_to_use)
        bibliography_data.append(result)

        if result.get("Error"):
            failure_count += 1
        else:
            success_count += 1

        # Simple progress update to console
        print(f"Progress: {processed_count}/{total_isbns} (Success: {success_count}, Fail: {failure_count})", end='\r')

    print("\nProcessing complete.") # Newline after progress updates

    if bibliography_data:
        write_success = write_bibliography_to_excel(bibliography_data, args.output_excel, sheet_name=CONFIG["output_sheet_name"])
        if write_success:
            logging.info(f"Bibliography data successfully written to {args.output_excel}")
        else:
            logging.error(f"Failed to write bibliography data to {args.output_excel}")
    else:
        logging.info("No bibliography data was generated to write.")

    logging.info(f"--- Summary ---")
    logging.info(f"Total ISBNs processed: {processed_count}")
    logging.info(f"Successful lookups: {success_count}")
    logging.info(f"Failed lookups: {failure_count}")
    print(f"\nSummary:\nTotal ISBNs processed: {processed_count}\nSuccessful lookups: {success_count}\nFailed lookups: {failure_count}")


if __name__ == "__main__":
    main()
