# Main script for the ISBN Bibliographer application
import argparse
import logging
import time
import json # Added for loading config if used later
import os # For checking file existence

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


def run_batch_mode(input_excel_path: str, output_excel_path: str, config: dict):
    """Handles the original batch processing from an input Excel file."""
    logging.info(f"Running in Batch Mode.")
    logging.info(f"Input file: {input_excel_path}")
    logging.info(f"Output file: {output_excel_path}")
    logging.info(f"Using ISBN column: {config['isbn_column_name']}")

    raw_isbns = read_isbns_from_excel(input_excel_path, isbn_column_name=config["isbn_column_name"])

    if not raw_isbns:
        logging.warning("No ISBNs found in the input file or an error occurred during reading for batch mode.")
        print("No ISBNs to process from input file. Exiting batch mode.")
        # Optionally, write an empty file or a file with just headers if output_excel_path is new
        # write_bibliography_to_excel([], output_excel_path, sheet_name=config["output_sheet_name"])
        return

    bibliography_data = []
    total_isbns = len(raw_isbns)
    processed_count = 0
    success_count = 0
    failure_count = 0

    for isbn_raw in raw_isbns:
        processed_count += 1
        # logging.info(f"Processing ISBN {processed_count}/{total_isbns}: {isbn_raw}") # Already logged in process_single_isbn

        if processed_count > 1 and config["rate_limit_delay"] > 0:
            logging.debug(f"Waiting for {config['rate_limit_delay']}s before next API call...")
            time.sleep(config["rate_limit_delay"])

        api_to_use = config["api_source_priority"][0] if config["api_source_priority"] else "google"
        result = process_single_isbn(isbn_raw, api_key=config["google_books_api_key"], preferred_api=api_to_use)
        bibliography_data.append(result)

        if result.get("Error"):
            failure_count += 1
        else:
            success_count += 1

        print(f"Batch Progress: {processed_count}/{total_isbns} (Success: {success_count}, Fail: {failure_count})", end='\r')

    print("\nBatch processing complete.")

    if bibliography_data:
        write_success = write_bibliography_to_excel(bibliography_data, output_excel_path, sheet_name=config["output_sheet_name"])
        if write_success:
            logging.info(f"Batch bibliography data successfully written to {output_excel_path}")
        else:
            logging.error(f"Failed to write batch bibliography data to {output_excel_path}")
    else:
        logging.info("No bibliography data was generated from batch mode to write.")

    logging.info(f"--- Batch Mode Summary ---")
    logging.info(f"Total ISBNs processed: {processed_count}")
    logging.info(f"Successful lookups: {success_count}")
    logging.info(f"Failed lookups: {failure_count}")
    print(f"\nBatch Summary:\nTotal ISBNs processed: {processed_count}\nSuccessful lookups: {success_count}\nFailed lookups: {failure_count}")


def run_hid_scanner_mode(output_filepath: str, config: dict):
    """Handles ISBN processing via simulated HID scanner input."""
    logging.info(f"Activating HID Scanner Mode. Output will be to {output_filepath}")
    print("HID Scanner Mode Activated.")
    print(f"Scanned ISBNs will be processed and saved/appended to: {output_filepath}")
    print("Type 'QUITSCAN' (all caps) and press Enter to finish scanning and save.")

    bibliography_data = [] # This will hold all data (existing + new)

    # --- Excel Handling: Load existing data if file exists ---
    if os.path.exists(output_filepath):
        try:
            logging.info(f"Output file {output_filepath} exists. Attempting to load existing data.")
            # Read all columns as string to avoid type issues, especially with ISBNs and years
            # Ensure openpyxl is used for xlsx
            df_existing = pd.read_excel(output_filepath, sheet_name=config["output_sheet_name"], dtype=str, engine='openpyxl')
            # Convert pandas' NaT or numpy.nan to empty strings or None for consistency before to_dict
            # Using fillna('') ensures that all "empty" cells become empty strings.
            df_existing = df_existing.fillna('')
            bibliography_data = df_existing.to_dict('records') # List of dictionaries
            logging.info(f"Loaded {len(bibliography_data)} existing records from '{output_filepath}'.")
            print(f"Loaded {len(bibliography_data)} existing records from '{output_filepath}'.")
        except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
            logging.info(f"Output file {output_filepath} not found (should not happen if os.path.exists passed). Starting fresh.")
            bibliography_data = []
        except ValueError as ve: # Handles issues like "Excel file format cannot be determined" or sheet not found
            logging.error(f"ValueError reading {output_filepath}: {ve}. It might be corrupted, not an Excel file, or sheet '{config['output_sheet_name']}' missing. Starting with an empty list.")
            print(f"Warning: Could not properly read existing Excel file at '{output_filepath}'. Check file or sheet name. Starting fresh for this session.")
            bibliography_data = []
        except Exception as e:
            logging.error(f"An unexpected error occurred loading existing data from {output_filepath}: {e}. Starting with an empty list.")
            print(f"Warning: An error occurred reading existing Excel file. Starting fresh for this session.")
            bibliography_data = []
    else:
        logging.info(f"Output file {output_filepath} does not exist. Starting fresh.")
        print(f"Output file '{output_filepath}' will be created.")
        bibliography_data = []
    # --- End of Excel Handling ---

    scanned_items_session = [] # Collects only items from this new session to be appended
    processed_count = 0
    success_count = 0
    failure_count = 0

    while True:
        try:
            scanned_input = input("Scan ISBN (or type 'QUITSCAN' to finish): ").strip()
        except EOFError: # Handle if input stream closes unexpectedly (e.g. piping)
            logging.warning("EOF received. Exiting scanner mode.")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            logging.info("Keyboard interrupt received. Exiting scanner mode.")
            print("\nScan interrupted. Finishing up...")
            break

        if scanned_input.upper() == 'QUITSCAN':
            logging.info("QUITSCAN command received. Exiting scanner mode.")
            break

        if not scanned_input:
            logging.debug("Empty scan ignored.")
            continue

        processed_count += 1
        logging.info(f"Processing scanned input: {scanned_input}")

        # Basic rate limiting (might be less critical for manual scanning but good to keep)
        if processed_count > 1 and config["rate_limit_delay"] > 0: # Check against total processed in session
            logging.debug(f"Waiting for {config['rate_limit_delay']}s before next API call...")
            time.sleep(config["rate_limit_delay"])

        api_to_use = config["api_source_priority"][0] if config["api_source_priority"] else "google"
        result = process_single_isbn(scanned_input, api_key=config["google_books_api_key"], preferred_api=api_to_use)

        # For this step, we just add to session items. Combining with existing data is next.
        scanned_items_session.append(result)

        if result.get("Error"):
            failure_count += 1
            logging.warning(f"Failed to process scanned ISBN {scanned_input}: {result.get('Error')}")
            print(f"Error for {scanned_input}: {result.get('Error')}")
        else:
            success_count += 1
            logging.info(f"Successfully processed scanned ISBN {scanned_input}: {result.get('Title')}")
            print(f"Successfully processed {scanned_input}: {result.get('Title', 'N/A')}")

        # Progress for current session
        print(f"Session Scans: {processed_count} (Success: {success_count}, Fail: {failure_count}) | Type QUITSCAN to save & exit.")

    logging.info("Finished HID scanning.")

    if scanned_items_session:
        bibliography_data.extend(scanned_items_session) # Add newly scanned items to the main list
        logging.info(f"Added {len(scanned_items_session)} new items to the bibliography list.")

    if bibliography_data: # If there's any data (old or new)
        total_records_to_write = len(bibliography_data)
        print(f"\nSaving {total_records_to_write} total records to {output_filepath}...")
        write_success = write_bibliography_to_excel(bibliography_data, output_filepath, sheet_name=config["output_sheet_name"])
        if write_success:
            logging.info(f"HID scanner bibliography data ({total_records_to_write} records) successfully written to {output_filepath}")
            print("Data saved successfully.")
        else:
            logging.error(f"Failed to write HID scanner bibliography data to {output_filepath}")
            print("Error saving data.")
    else:
        logging.info("No data (neither existing nor newly scanned) to write.")
        print("No data to save.")

    logging.info(f"--- HID Scanner Mode Summary (Session: {processed_count} scans, {success_count} success, {failure_count} fail) ---")
    logging.info(f"Total ISBNs processed in session: {processed_count}")
    logging.info(f"Successful lookups in session: {success_count}")
    logging.info(f"Failed lookups in session: {failure_count}")
    print(f"\nSession Summary:\nTotal Scans: {processed_count}\nSuccessful: {success_count}\nFailed: {failure_count}")


def main():
    parser = argparse.ArgumentParser(description="ISBN Bibliographer: Process ISBNs and retrieve book information.")

    # Group for mutually exclusive modes: batch file input vs scanner input
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input_excel", help="Path to the input Excel file (.xlsx, .xls) for batch processing.")
    group.add_argument("--scanner", action="store_true", help="Activate HID barcode scanner mode. Output file must be specified via --output_excel.")

    parser.add_argument("--output_excel", help="Path for the output Excel file (.xlsx). Required for all modes.", required=True)
    parser.add_argument("--config", help="Path to a JSON configuration file.", default=None)

    args = parser.parse_args()

    load_config(args.config) # Load config if provided
    logging.info(f"Starting ISBN Bibliography process...")

    if args.scanner:
        logging.info("Scanner mode selected.")
        # For now, this defaults to HID. Later, we might add another arg like --scanner_type if camera is added.
        run_hid_scanner_mode(args.output_excel, CONFIG)
    elif args.input_excel:
        logging.info("Batch mode selected.")
        run_batch_mode(args.input_excel, args.output_excel, CONFIG)
    else:
        # This case should ideally not be reached due to the mutually exclusive group being required.
        parser.print_help()
        logging.error("No valid mode selected (e.g., --input_excel or --scanner). This shouldn't happen.")
        print("Error: You must specify either --input_excel for batch mode or --scanner for scanner mode.")


if __name__ == "__main__":
    main()
