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

3.  **Configuration (Optional but Recommended for Google Books API):**
    Create a `config.json` file in the `isbn_bibliographer` directory by copying `config.json.template`.
    ```json
    {
        "google_books_api_key": "YOUR_GOOGLE_BOOKS_API_KEY",
        "isbn_column_name": "ISBN",
        "output_sheet_name": "Bibliography",
        "rate_limit_delay": 1
    }
    ```
    Replace `"YOUR_GOOGLE_BOOKS_API_KEY"` with your actual Google Books API key if you have one. While the Google Books API can be used without a key, it's subject to stricter anonymous quota limits. An API key allows for more requests. You can obtain one from the [Google Cloud Console](https://console.cloud.google.com/apis/library/books.googleapis.com).

## Usage

Run the script from the `isbn_bibliographer` directory:

```bash
python main.py <input_excel_file> <output_excel_file> [--config <path_to_config.json>]
```

**Examples:**

1.  **Basic usage (assuming `config.json` is in the same directory or using default settings):**
    ```bash
    python main.py path/to/your_isbns.xlsx path/to/output_bibliography.xlsx
    ```

2.  **With a specific configuration file:**
    ```bash
    python main.py input.xlsx output.xlsx --config my_custom_config.json
    ```

### Input Excel File Format

The input Excel file should have a column containing ISBN numbers. By default, the script looks for a column named "ISBN". This can be changed in the `config.json` file (`isbn_column_name` setting).

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
