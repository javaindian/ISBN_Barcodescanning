import pandas as pd
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_isbns_from_excel(filepath: str, isbn_column_name: str = 'ISBN') -> List[str]:
    """
    Reads ISBNs from a specified column in an Excel file.

    Args:
        filepath (str): The path to the Excel file (.xlsx or .xls).
        isbn_column_name (str): The name of the column containing ISBNs. Defaults to 'ISBN'.

    Returns:
        List[str]: A list of ISBNs found in the specified column. Returns empty list on error.
    """
    isbns: List[str] = []
    try:
        # Determine the engine based on file extension
        engine = 'openpyxl' if filepath.endswith('.xlsx') else 'xlrd'
        df = pd.read_excel(filepath, engine=engine, dtype={isbn_column_name: str})

        if isbn_column_name not in df.columns:
            logging.error(f"Column '{isbn_column_name}' not found in the Excel file: {filepath}")
            possible_columns = ", ".join(df.columns)
            logging.info(f"Available columns are: {possible_columns}")
            return isbns

        # Drop rows where ISBN is NaN, convert to string, and filter out empty strings
        isbns = df[isbn_column_name].dropna().astype(str).str.strip().tolist()
        isbns = [isbn for isbn in isbns if isbn] # Filter out any empty strings after stripping

        logging.info(f"Successfully read {len(isbns)} ISBNs from '{filepath}', column '{isbn_column_name}'.")

    except FileNotFoundError:
        logging.error(f"Excel file not found: {filepath}")
    except pd.errors.EmptyDataError:
        logging.error(f"No data found in Excel file: {filepath}")
    except KeyError:
        # This might happen if dtype specification fails or column name is incorrect in a way not caught above
        logging.error(f"Error accessing column '{isbn_column_name}'. Ensure it exists and data is consistent.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading Excel file '{filepath}': {e}")

    return isbns

def write_bibliography_to_excel(data: List[Dict[str, Any]], filepath: str, sheet_name: str = 'Bibliography') -> bool:
    """
    Writes bibliography data to an Excel file.

    Args:
        data (List[Dict[str, Any]]): A list of dictionaries, where each dictionary represents a book's bibliography.
        filepath (str): The path to the output Excel file (.xlsx).
        sheet_name (str): The name of the sheet to write data to. Defaults to 'Bibliography'.

    Returns:
        bool: True if writing was successful, False otherwise.
    """
    if not data:
        logging.warning("No data provided to write to Excel.")
        # Optionally, create an empty file with headers if desired, or just return False
        # For now, let's consider it not a success if there's no data.
        # However, creating an empty file might be valid in some scenarios.
        # To create an empty file with headers, one would need to know the headers.
        # df = pd.DataFrame(columns=EXPECTED_HEADERS)
        # df.to_excel(filepath, sheet_name=sheet_name, index=False, engine='openpyxl')
        return False

    try:
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name=sheet_name, index=False, engine='openpyxl')
        logging.info(f"Successfully wrote {len(data)} records to '{filepath}', sheet '{sheet_name}'.")
        return True
    except Exception as e:
        logging.error(f"An error occurred while writing to Excel file '{filepath}': {e}")
        return False

if __name__ == '__main__':
    # Create dummy Excel files for testing
    # Test read_isbns_from_excel
    sample_input_file_xlsx = "sample_isbns.xlsx"
    sample_input_file_xls = "sample_isbns.xls"

    # Data for XLSX
    df_input_xlsx = pd.DataFrame({
        'ISBN': ["978-0306406157", " 0306406152 ", None, "9780439023528", ""],
        'Title': ["Book A", "Book B", "Book C", "Book D", "Book E"],
        'OtherData': [1, 2, 3, 4, 5]
    })
    df_input_xlsx.to_excel(sample_input_file_xlsx, index=False, engine='openpyxl')

    # Data for XLS (requires xlwt to write, xlrd to read)
    # For simplicity, we'll assume xlwt is available if testing this part.
    # If not, this part of the test might fail or need adjustment.
    try:
        df_input_xls = pd.DataFrame({
            'ISBN': ["0-13-235088-2", "0-596-52068-9", None],
            'Book Name': ["Clean Code", "Python Cookbook", "Another Book"]
        })
        df_input_xls.to_excel(sample_input_file_xls, index=False) # Default engine will try xlwt
        xls_writable = True
    except Exception as e:
        logging.warning(f"Could not create sample XLS file, xlwt might be missing: {e}")
        xls_writable = False

    print("--- Testing read_isbns_from_excel ---")
    isbns_xlsx = read_isbns_from_excel(sample_input_file_xlsx)
    print(f"ISBNs from '{sample_input_file_xlsx}': {isbns_xlsx}")
    expected_isbns_xlsx = ["9780306406157", "0306406152", "9780439023528"]
    assert sorted(isbns_xlsx) == sorted(expected_isbns_xlsx), f"Expected {expected_isbns_xlsx} but got {isbns_xlsx}"

    isbns_xlsx_custom_col = read_isbns_from_excel(sample_input_file_xlsx, isbn_column_name='Title')
    print(f"ISBNs from '{sample_input_file_xlsx}' (column 'Title'): {isbns_xlsx_custom_col}")
    # Based on dummy data, 'Title' column contains "Book A", "Book B", etc.
    expected_titles_as_isbns = ["Book A", "Book B", "Book C", "Book D", "Book E"]
    assert sorted(isbns_xlsx_custom_col) == sorted(expected_titles_as_isbns)

    if xls_writable:
        isbns_xls = read_isbns_from_excel(sample_input_file_xls, isbn_column_name='ISBN')
        print(f"ISBNs from '{sample_input_file_xls}': {isbns_xls}")
        expected_isbns_xls = ["0132350882", "0596520689"] # Normalized versions
        # The read function currently doesn't normalize, it just strips. Normalization is a separate step.
        # So, the expected output should match the stripped values from the file.
        expected_isbns_xls_raw = ["0-13-235088-2", "0-596-52068-9"]
        assert sorted(isbns_xls) == sorted(expected_isbns_xls_raw), f"Expected {expected_isbns_xls_raw} but got {isbns_xls}"


    print("\n--- Testing write_bibliography_to_excel ---")
    sample_output_file = "sample_bibliography.xlsx"
    sample_data = [
        {"Title": "Book 1", "Author": "Author A", "ISBN-13": "978-1234567890", "Year": "2020"},
        {"Title": "Book 2", "Author": "Author B", "ISBN-13": "978-0987654321", "Publisher": "Pub B"},
        {"Title": "Failed Lookup", "ISBN-13": "978-1111111111", "Error": "API lookup failed"}
    ]

    success_write = write_bibliography_to_excel(sample_data, sample_output_file)
    print(f"Writing to '{sample_output_file}' successful: {success_write}")
    assert success_write

    # Test reading back the written file to verify content (optional, but good for robust testing)
    if success_write:
        df_written = pd.read_excel(sample_output_file, engine='openpyxl')
        # Convert to list of dicts for easier comparison, handling NaNs
        written_data = df_written.astype(object).where(pd.notnull(df_written), None).to_dict('records')
        # print(f"Data read back: {written_data}")
        # This comparison can be tricky due to float NaNs vs None, etc.
        # For simplicity, we'll just check the number of records and a few key values.
        assert len(written_data) == len(sample_data)
        assert written_data[0]['Title'] == sample_data[0]['Title']
        assert written_data[1]['Publisher'] == sample_data[1]['Publisher']
        if pd.isna(written_data[0].get('Publisher')): # Author A has no publisher in sample_data
             assert sample_data[0].get('Publisher') is None

    # Test writing empty data
    print("\n--- Testing write_bibliography_to_excel with empty data ---")
    empty_data = []
    success_write_empty = write_bibliography_to_excel(empty_data, "empty_output.xlsx")
    print(f"Writing empty data successful: {success_write_empty}")
    # As per current implementation, this returns False and logs a warning.
    assert not success_write_empty

    # Clean up dummy files (optional)
    import os
    try:
        os.remove(sample_input_file_xlsx)
        if xls_writable: os.remove(sample_input_file_xls)
        os.remove(sample_output_file)
        if not success_write_empty: # if it didn't create the file
            if os.path.exists("empty_output.xlsx"): os.remove("empty_output.xlsx")
        print("Cleaned up sample files.")
    except OSError as e:
        logging.warning(f"Could not clean up all sample files: {e}")
