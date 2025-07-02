import unittest
from ..modules.isbn_validator import (
    normalize_isbn,
    is_valid_isbn10,
    is_valid_isbn13,
    to_isbn10,
    to_isbn13
)

class TestISBNValidator(unittest.TestCase):

    def test_normalize_isbn(self):
        self.assertEqual(normalize_isbn("978-0-306-40615-7"), "9780306406157")
        self.assertEqual(normalize_isbn(" 0 306 40615 2 "), "0306406152")
        self.assertEqual(normalize_isbn("030640615X"), "030640615X") # Should keep X as is
        self.assertEqual(normalize_isbn(""), "")

    def test_is_valid_isbn10(self):
        self.assertTrue(is_valid_isbn10("0306406152"))
        self.assertTrue(is_valid_isbn10("0-306-40615-2"))
        self.assertTrue(is_valid_isbn10("0439023521")) # Ends with X
        self.assertTrue(is_valid_isbn10("043902352X")) # Valid X
        self.assertFalse(is_valid_isbn10("0306406155")) # Invalid check digit
        self.assertFalse(is_valid_isbn10("123456789")) # Too short
        self.assertFalse(is_valid_isbn10("12345678901")) # Too long
        self.assertFalse(is_valid_isbn10("123456789Y")) # Invalid character
        self.assertFalse(is_valid_isbn10("030640615x")) # Small x should be handled by normalize

    def test_is_valid_isbn13(self):
        self.assertTrue(is_valid_isbn13("9780306406157"))
        self.assertTrue(is_valid_isbn13("978-0-306-40615-7"))
        self.assertFalse(is_valid_isbn13("9780306406150")) # Invalid check digit
        self.assertFalse(is_valid_isbn13("123456789012")) # Too short
        self.assertFalse(is_valid_isbn13("12345678901234")) # Too long
        self.assertFalse(is_valid_isbn13("978030640615X")) # Invalid character
        self.assertTrue(is_valid_isbn13("9791234567896")) # Valid 979 prefix example (check digit calculated for this)


    def test_to_isbn13(self):
        self.assertEqual(to_isbn13("0306406152"), "9780306406157")
        self.assertEqual(to_isbn13("0-439-02352-1"), "9780439023528") # With hyphens and X
        self.assertIsNone(to_isbn13("0306406155")) # Invalid ISBN-10
        self.assertIsNone(to_isbn13("12345")) # Too short

    def test_to_isbn10(self):
        self.assertEqual(to_isbn10("9780306406157"), "0306406152")
        self.assertEqual(to_isbn10("978-0-439-02352-8"), "0439023521") # With hyphens
        self.assertIsNone(to_isbn10("9780306406150")) # Invalid ISBN-13
        self.assertIsNone(to_isbn10("9791234567896")) # Valid ISBN-13 but not convertible (not 978 prefix)
        self.assertIsNone(to_isbn10("12345")) # Too short

if __name__ == '__main__':
    unittest.main()
