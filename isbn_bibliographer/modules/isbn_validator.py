import re

def normalize_isbn(isbn: str) -> str:
    """Removes hyphens and whitespace from an ISBN string."""
    return isbn.replace("-", "").replace(" ", "").upper()

def is_valid_isbn10(isbn: str) -> bool:
    """Validates an ISBN-10 number."""
    isbn = normalize_isbn(isbn)
    if not re.match(r"^\d{9}[\dX]$", isbn):
        return False

    total = 0
    for i in range(9):
        total += int(isbn[i]) * (10 - i)

    check_digit = isbn[9]
    if check_digit == 'X':
        total += 10
    else:
        total += int(check_digit)

    return total % 11 == 0

def is_valid_isbn13(isbn: str) -> bool:
    """Validates an ISBN-13 number."""
    isbn = normalize_isbn(isbn)
    if not re.match(r"^\d{13}$", isbn):
        return False

    total = 0
    for i in range(12):
        digit = int(isbn[i])
        total += digit * (1 if i % 2 == 0 else 3)

    check_digit = int(isbn[12])
    return (10 - (total % 10)) % 10 == check_digit

def to_isbn13(isbn10: str) -> str | None:
    """Converts an ISBN-10 to ISBN-13."""
    isbn10 = normalize_isbn(isbn10)
    if not is_valid_isbn10(isbn10):
        return None

    prefix = "978" + isbn10[:-1]
    total = 0
    for i in range(12):
        digit = int(prefix[i])
        total += digit * (1 if i % 2 == 0 else 3)

    check_digit = (10 - (total % 10)) % 10
    return prefix + str(check_digit)

def to_isbn10(isbn13: str) -> str | None:
    """Converts an ISBN-13 to ISBN-10."""
    isbn13 = normalize_isbn(isbn13)
    if not is_valid_isbn13(isbn13):
        return None

    if not isbn13.startswith("978"):
        # Cannot be converted to ISBN-10 if not starting with 978
        return None

    isbn10_stem = isbn13[3:-1]
    total = 0
    for i in range(9):
        total += int(isbn10_stem[i]) * (10 - i)

    check_digit_val = (11 - (total % 11)) % 11
    check_digit = 'X' if check_digit_val == 10 else str(check_digit_val)

    return isbn10_stem + check_digit

if __name__ == '__main__':
    # Test cases
    test_isbn10_valid = "0306406152"
    test_isbn10_invalid = "0306406155"
    test_isbn10_hyphen = "0-306-40615-2"
    test_isbn10_with_X = "0439023521" # The Hunger Games

    test_isbn13_valid = "9780306406157"
    test_isbn13_invalid = "9780306406150"
    test_isbn13_hyphen = "978-0-306-40615-7"

    print(f"'{test_isbn10_valid}' (normalized: {normalize_isbn(test_isbn10_valid)}) is valid ISBN-10: {is_valid_isbn10(test_isbn10_valid)}")
    print(f"'{test_isbn10_invalid}' is valid ISBN-10: {is_valid_isbn10(test_isbn10_invalid)}")
    print(f"'{test_isbn10_hyphen}' is valid ISBN-10: {is_valid_isbn10(test_isbn10_hyphen)}")
    print(f"'{test_isbn10_with_X}' is valid ISBN-10: {is_valid_isbn10(test_isbn10_with_X)}")


    print(f"'{test_isbn13_valid}' (normalized: {normalize_isbn(test_isbn13_valid)}) is valid ISBN-13: {is_valid_isbn13(test_isbn13_valid)}")
    print(f"'{test_isbn13_invalid}' is valid ISBN-13: {is_valid_isbn13(test_isbn13_invalid)}")
    print(f"'{test_isbn13_hyphen}' is valid ISBN-13: {is_valid_isbn13(test_isbn13_hyphen)}")

    # Test conversions
    converted_to_13 = to_isbn13(test_isbn10_valid)
    print(f"ISBN-10 '{test_isbn10_valid}' to ISBN-13: {converted_to_13}, expected: {test_isbn13_valid}")
    if converted_to_13:
        print(f"Converted ISBN-13 '{converted_to_13}' is valid: {is_valid_isbn13(converted_to_13)}")

    converted_to_10 = to_isbn10(test_isbn13_valid)
    print(f"ISBN-13 '{test_isbn13_valid}' to ISBN-10: {converted_to_10}, expected: {test_isbn10_valid}")
    if converted_to_10:
        print(f"Converted ISBN-10 '{converted_to_10}' is valid: {is_valid_isbn10(converted_to_10)}")

    # Test conversion for ISBN-10 with 'X'
    isbn10_x = "0439023521" # The Hunger Games
    expected_isbn13_for_x = "9780439023528"
    converted_to_13_from_x = to_isbn13(isbn10_x)
    print(f"ISBN-10 '{isbn10_x}' to ISBN-13: {converted_to_13_from_x}, expected: {expected_isbn13_for_x}")
    if converted_to_13_from_x:
        print(f"Converted ISBN-13 '{converted_to_13_from_x}' is valid: {is_valid_isbn13(converted_to_13_from_x)}")

    converted_to_10_from_x_isbn13 = to_isbn10(expected_isbn13_for_x)
    print(f"ISBN-13 '{expected_isbn13_for_x}' to ISBN-10: {converted_to_10_from_x_isbn13}, expected: {isbn10_x}")
    if converted_to_10_from_x_isbn13:
         print(f"Converted ISBN-10 '{converted_to_10_from_x_isbn13}' is valid: {is_valid_isbn10(converted_to_10_from_x_isbn13)}")

    # Test invalid conversion
    invalid_isbn10_for_conversion = "1234567890"
    print(f"to_isbn13 for invalid ISBN-10 '{invalid_isbn10_for_conversion}': {to_isbn13(invalid_isbn10_for_conversion)}")

    invalid_isbn13_for_conversion = "9781234567890" # Invalid check digit
    print(f"to_isbn10 for invalid ISBN-13 '{invalid_isbn13_for_conversion}': {to_isbn10(invalid_isbn13_for_conversion)}")

    non_978_isbn13 = "9791028902657" # Valid ISBN-13 but doesn't start with 978
    print(f"'{non_978_isbn13}' is valid ISBN-13: {is_valid_isbn13(non_978_isbn13)}")
    print(f"to_isbn10 for non-978 ISBN-13 '{non_978_isbn13}': {to_isbn10(non_978_isbn13)}")
