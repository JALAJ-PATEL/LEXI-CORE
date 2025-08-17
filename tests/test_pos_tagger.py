"""
Unit tests for the POSTagger class
"""
import unittest
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from linguistic_analysis.pos_tagger import POSTagger


class TestPOSTagger(unittest.TestCase):
    """Test cases for the POSTagger class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Use the test data directory
        test_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.pos_tagger = POSTagger(test_data_dir)
    
    def test_basic_tagging(self):
        """Test basic POS tagging functionality"""
        tokens = ["The", "cat", "is", "running", "quickly"]
        result = self.pos_tagger.tag_tokens(tokens)
        
        # Check that we get tuples of (token, tag)
        self.assertEqual(len(result), 5)
        for token, tag in result:
            self.assertIsInstance(token, str)
            self.assertIsInstance(tag, str)
    
    def test_known_words(self):
        """Test tagging of known words from dictionary"""
        # Test some words that should be in the dictionary
        self.assertEqual(self.pos_tagger.tag_word("cat"), "NOUNS")
        self.assertEqual(self.pos_tagger.tag_word("run"), "VERBS")
        self.assertEqual(self.pos_tagger.tag_word("good"), "ADJECTIVES")
        self.assertEqual(self.pos_tagger.tag_word("quickly"), "ADVERBS")
    
    def test_suffix_rules(self):
        """Test POS tagging based on suffix rules"""
        # Words with common suffixes
        self.assertIn(self.pos_tagger.tag_word("running"), ["VERB", "VERBS"])
        self.assertIn(self.pos_tagger.tag_word("beautiful"), ["ADJECTIVE", "ADJECTIVES"])
        self.assertIn(self.pos_tagger.tag_word("happiness"), ["NOUN", "NOUNS"])
        self.assertIn(self.pos_tagger.tag_word("carefully"), ["ADVERB", "ADVERBS"])
    
    def test_unknown_words(self):
        """Test tagging of unknown words"""
        # Unknown words should get default tags
        result = self.pos_tagger.tag_word("xyzabc")
        self.assertIsInstance(result, str)
        self.assertIn(result, ["NOUN", "UNKNOWN"])
    
    def test_capitalized_words(self):
        """Test tagging of capitalized words"""
        # Capitalized words might be proper nouns
        result = self.pos_tagger.tag_word("John")
        self.assertIsInstance(result, str)
    
    def test_numbers_and_punctuation(self):
        """Test tagging of numbers and punctuation"""
        self.assertEqual(self.pos_tagger.tag_word("123"), "NUMBER")
        self.assertEqual(self.pos_tagger.tag_word("!"), "PUNCTUATION")
        self.assertEqual(self.pos_tagger.tag_word("hello123"), "IDENTIFIER")
    
    def test_contextual_rules(self):
        """Test contextual POS tagging rules"""
        # Test determiner + noun pattern
        tokens = ["the", "cat"]
        result = self.pos_tagger.tag_tokens(tokens)
        
        # The second word after 'the' should be tagged as noun
        self.assertEqual(result[1][1], "NOUN")
    
    def test_pos_stats(self):
        """Test POS statistics generation"""
        tokens = ["The", "quick", "brown", "fox", "jumps"]
        tagged = self.pos_tagger.tag_tokens(tokens)
        stats = self.pos_tagger.get_pos_stats(tagged)
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(sum(stats.values()), len(tokens))
    
    def test_empty_input(self):
        """Test POS tagging with empty input"""
        result = self.pos_tagger.tag_tokens([])
        self.assertEqual(result, [])
        
        result = self.pos_tagger.tag_word("")
        self.assertEqual(result, "UNKNOWN")


if __name__ == '__main__':
    unittest.main()
