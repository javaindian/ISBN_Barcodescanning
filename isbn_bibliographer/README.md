# ISBN Bibliographer

A Python application to process ISBNs from an Excel file, retrieve comprehensive book information via web APIs (initially Google Books API), and output complete bibliography records to an Excel file.

## Features (Current and Planned)

*   Reads ISBNs from `.xlsx` or `.xls` files.
*   Validates and normalizes ISBN-10 and ISBN-13 numbers.
*   Converts between ISBN-10 and ISBN-13.
*   Fetches book data using the Google Books API.
*   Formats retrieved data into a structured bibliography.
*   Writes bibliography data to an `.xlsx` Excel file.
*   Basic logging for operations and errors.
*   Command-line interface.
*   Configurable via a JSON file.
*   Unit tests for core modules.

## Prerequisites

*   Python 3.8+
*   Required Python libraries (see `requirements.txt` - *to be created*)

```
pandas
openpyxl
xlrd  # For reading .xls files
requests
```

## Setup

1.  **Clone the repository (if applicable) or download the files.**
2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configuration (Optional):**
    Create a `config.json` file in the `isbn_bibliographer` directory by copying `config.json.template`.
    ```json
    {
        "isbn_column_name": "ISBN",
        "output_sheet_name": "Bibliography",
        "api_source_priority": ["google"],
        "rate_limit_delay": 1
    }
    ```
    The application uses unauthenticated requests to the Google Books API by default, so an API key is not required. The `config.json` file can be used to customize other parameters like the ISBN column name in input files or the default rate limiting delay.

## Usage

The script can be run in two main modes: **Batch Mode** (processing an input Excel file) or **Scanner Mode** (processing ISBNs entered via keyboard emulation, e.g., from a USB HID barcode scanner).

### General Command Structure

```bash
python main.py [MODE_ARGUMENT] --output_excel <output_file.xlsx> [--config <path_to_config.json>]
```
*   `--output_excel <output_file.xlsx>`: (Required for all modes) Specifies the Excel file where bibliography data will be saved.
*   `--config <path_to_config.json>`: (Optional) Path to a JSON configuration file.

### Mode Arguments (Choose One)

1.  **Batch Mode**:
    *   `--input_excel <input_file.xlsx>`: Specifies the input Excel file containing ISBNs.

    **Example (Batch Mode):**
    ```bash
    python main.py --input_excel path/to/your_isbns.xlsx --output_excel path/to/output_bibliography.xlsx
    ```

2.  **HID Scanner Mode**:
    *   `--scanner`: Activates the HID scanner mode. The script will prompt for ISBNs to be "scanned" (typed in and Enter pressed).

    **Example (Scanner Mode):**
    ```bash
    python main.py --scanner --output_excel path/to/output_bibliography.xlsx
    ```
    In scanner mode:
    *   The script will prompt you to enter ISBNs one by one.
    *   Type `QUITSCAN` (all caps) and press Enter to finish the scanning session and save the data.
    *   If the output Excel file already exists, new scans will be appended to the existing data. Otherwise, a new file will be created.

### Input Excel File Format (for Batch Mode)

The input Excel file for batch mode should have a column containing ISBN numbers. By default, the script looks for a column named "ISBN". This can be changed in the `config.json` file (`isbn_column_name` setting).

Example `input.xlsx`:

| ISBN             | Title (Optional) | Other Info (Optional) |
|------------------|------------------|-----------------------|
| 9780306406157    |                  |                       |
| 0306406152       |                  |                       |
| 978-0439023528   | My Book          | Notes                 |
| invalid-isbn     |                  |                       |

### Output Excel File Format

The output Excel file will contain the retrieved bibliography information. If an ISBN lookup fails or an ISBN is invalid, an "Error" column will provide details.

Example `output_bibliography.xlsx`:

| Input ISBN     | Title                                | Authors      | Publisher     | Publication Year | ISBN-10  | ISBN-13     | Error                         | ... (other fields) |
|----------------|--------------------------------------|--------------|---------------|------------------|----------|-------------|-------------------------------|--------------------|
| 9780306406157  | [Book Title]                         | [Author(s)]  | [Publisher]   | [Year]           | [ISBN10] | 9780306406157 |                               | ...                |
| 0306406152     | [Book Title]                         | [Author(s)]  | [Publisher]   | [Year]           | 0306406152 | [ISBN13]    |                               | ...                |
| invalid-isbn   |                                      |              |               |                  |          |             | Invalid ISBN format           | ...                |
| 9780000000000  |                                      |              |               |                  |          |             | No data found by google API...| ...                |


## Running Tests

To run the unit tests, navigate to the project's root directory (`isbn_bibliographer`) and run:

```bash
python -m unittest discover tests
```
Or for individual test files:
```bash
python -m unittest tests.test_isbn_validator
python -m unittest tests.test_api_manager
```

## Building the Executable

This project can be packaged into a standalone executable using PyInstaller (which is included in `requirements.txt`).

1.  **Ensure PyInstaller is installed:**
    If you followed the setup instructions and installed via `requirements.txt`, PyInstaller should already be available in your virtual environment.

2.  **Navigate to the project's root directory (`isbn_bibliographer`).**

3.  **Run PyInstaller:**
    Open your terminal or command prompt in the `isbn_bibliographer` directory and execute the following command:
    ```bash
    pyinstaller --name isbn_bibliographer --onefile main.py
    ```
    *   `--name isbn_bibliographer`: Sets the name of the executable and related files.
    *   `--onefile`: Packages everything into a single executable file.
    *   `main.py`: Specifies the main script of the application.

4.  **Find the Executable:**
    After PyInstaller finishes, you will find the standalone executable in a new directory named `dist`.
    *   On Windows: `dist/isbn_bibliographer.exe`
    *   On macOS/Linux: `dist/isbn_bibliographer`

    You can copy this executable to another location and run it without needing a Python installation (though the target system must be compatible with the OS used for building).

## Project Structure

```
isbn_bibliographer/
├── main.py                     # Main executable script
├── modules/                    # Core logic modules
│   ├── __init__.py
│   ├── api_manager.py          # Handles API interactions
│   ├── bibliography_formatter.py # Formats API data
│   ├── excel_processor.py      # Reads/writes Excel files
│   └── isbn_validator.py       # ISBN validation and normalization
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_api_manager.py
│   └── test_isbn_validator.py
├── config.json.template        # Template for configuration
├── README.md                   # This file
└── requirements.txt            # (To be added) Python package dependencies
```

## Future Enhancements (from original requirements)

*   Support for more APIs (Open Library, WorldCat, etc.) with fallback.
*   Advanced rate limiting and retry mechanisms.
*   More comprehensive bibliography fields.
*   Citation generation (APA, MLA, Chicago).
*   Barcode scanner integration.
*   GUI.
*   Duplicate ISBN detection.
*   Caching results.
*   And more...
```
