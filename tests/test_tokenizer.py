"""
Unit tests for the Tokenizer class
"""
import unittest
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing.tokenizer import Tokenizer


class TestTokenizer(unittest.TestCase):
    """Test cases for the Tokenizer class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.tokenizer = Tokenizer()
    
    def test_basic_tokenization(self):
        """Test basic tokenization functionality"""
        text = "Hello world! How are you?"
        expected = ["Hello", "world", "!", "How", "are", "you", "?"]
        result = self.tokenizer.tokenize(text)
        self.assertEqual(result, expected)
    
    def test_empty_input(self):
        """Test tokenization with empty input"""
        result = self.tokenizer.tokenize("")
        self.assertEqual(result, [])
        
        result = self.tokenizer.tokenize("   ")
        self.assertEqual(result, [])
    
    def test_contractions(self):
        """Test tokenization with contractions"""
        text = "I don't think it's working."
        result = self.tokenizer.tokenize(text)
        self.assertIn("don't", result)
        self.assertIn("it's", result)
    
    def test_punctuation(self):
        """Test tokenization with various punctuation"""
        text = "Hello, world! How are you? I'm fine."
        result = self.tokenizer.tokenize(text)
        self.assertIn(",", result)
        self.assertIn("!", result)
        self.assertIn("?", result)
    
    def test_numbers(self):
        """Test tokenization with numbers"""
        text = "I have 123 apples and 45.67 oranges."
        result = self.tokenizer.tokenize(text)
        self.assertIn("123", result)
        self.assertIn("45", result)
        self.assertIn("67", result)
    
    def test_sentence_tokenization(self):
        """Test sentence-level tokenization"""
        text = "Hello world! How are you? I'm fine."
        result = self.tokenizer.tokenize_sentences(text)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ["Hello", "world"])
        self.assertEqual(result[1], ["How", "are", "you"])
        self.assertEqual(result[2], ["I'm", "fine"])
    
    def test_mixed_content(self):
        """Test tokenization with mixed content"""
        text = "Visit https://example.com or email test@example.com for more info!"
        result = self.tokenizer.tokenize(text)
        self.assertIn("https", result)
        self.assertIn("example", result)
        self.assertIn("com", result)
        self.assertIn("test", result)


if __name__ == '__main__':
    unittest.main()
