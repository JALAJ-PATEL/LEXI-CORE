"""
Text normalization: lowercasing, expanding contractions, cleaning
"""
import json
import os
from typing import List, Dict


class Normalizer:
    """
    Text normalizer for preprocessing text data
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data directory relative to this file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(current_dir, 'data')
        
        self.data_dir = data_dir
        self.contractions = self._load_contractions()
    
    def _load_contractions(self) -> Dict[str, str]:
        """Load contractions mapping from JSON file"""
        try:
            contractions_path = os.path.join(self.data_dir, 'contractions.json')
            with open(contractions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return empty dict if file not found or invalid
            return {}
    
    def normalize_text(self, text: str) -> str:
        """
        Apply all normalization steps to text
        
        Args:
            text (str): Input text to normalize
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Expand contractions
        text = self.expand_contractions(text)
        
        # Remove extra whitespace
        text = self._clean_whitespace(text)
        
        return text
    
    def expand_contractions(self, text: str) -> str:
        """
        Expand contractions in text
        
        Args:
            text (str): Input text with contractions
            
        Returns:
            str: Text with expanded contractions
        """
        if not text or not self.contractions:
            return text
        
        # Sort contractions by length (longest first) to avoid partial matches
        sorted_contractions = sorted(self.contractions.items(), 
                                   key=lambda x: len(x[0]), reverse=True)
        
        for contraction, expansion in sorted_contractions:
            # Case-insensitive replacement
            text = text.replace(contraction.lower(), expansion.lower())
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """
        Remove extra whitespace and normalize spacing
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        # Replace multiple spaces with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading and trailing whitespace
        return text.strip()
    
    def normalize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Normalize a list of tokens
        
        Args:
            tokens (List[str]): List of tokens to normalize
            
        Returns:
            List[str]: List of normalized tokens
        """
        normalized_tokens = []
        
        for token in tokens:
            normalized_token = self.normalize_text(token)
            if normalized_token:  # Only add non-empty tokens
                normalized_tokens.append(normalized_token)
        
        return normalized_tokens
