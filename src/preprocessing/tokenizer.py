"""
Tokenization logic using regex patterns
"""
import re
from typing import List


class Tokenizer:
    """
    A regex-based tokenizer for splitting text into tokens
    """
    
    def __init__(self):
        # Pattern to match words, contractions, punctuation, and numbers
        self.token_pattern = re.compile(r'\b\w+\b|[^\w\s]')
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize input text into a list of tokens
        
        Args:
            text (str): Input text to tokenize
            
        Returns:
            List[str]: List of tokens
        """
        if not text:
            return []
        
        # Find all tokens using the regex pattern
        tokens = self.token_pattern.findall(text)
        
        # Filter out empty tokens
        tokens = [token for token in tokens if token.strip()]
        
        return tokens
    
    def tokenize_sentences(self, text: str) -> List[List[str]]:
        """
        Tokenize text into sentences, then tokenize each sentence
        
        Args:
            text (str): Input text to tokenize
            
        Returns:
            List[List[str]]: List of sentences, each containing tokens
        """
        # Simple sentence splitting on periods, exclamation marks, and question marks
        sentence_pattern = re.compile(r'[.!?]+')
        sentences = sentence_pattern.split(text)
        
        tokenized_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                tokens = self.tokenize(sentence)
                if tokens:
                    tokenized_sentences.append(tokens)
        
        return tokenized_sentences
