"""
Dictionary and suffix-based Part-of-Speech tagger
"""
import json
import os
from typing import List, Tuple, Dict


class POSTagger:
    """
    Rule-based Part-of-Speech tagger using dictionary lookup and suffix rules
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data directory relative to this file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(current_dir, 'data')
        
        self.data_dir = data_dir
        self.pos_dictionary = self._load_pos_dictionary()
        self.suffix_rules = self._load_suffix_rules()
    
    def _load_pos_dictionary(self) -> Dict[str, List[str]]:
        """Load POS dictionary from JSON file"""
        try:
            dict_path = os.path.join(self.data_dir, 'pos_dictionary.json')
            with open(dict_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _load_suffix_rules(self) -> Dict[str, str]:
        """Load suffix rules from JSON file"""
        try:
            rules_path = os.path.join(self.data_dir, 'pos_suffix_rules.json')
            with open(rules_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('suffix_priority', {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def tag_word(self, word: str) -> str:
        """
        Tag a single word with its part of speech
        
        Args:
            word (str): Word to tag
            
        Returns:
            str: POS tag
        """
        if not word:
            return 'UNKNOWN'
        
        word_lower = word.lower()
        
        # First, check dictionary lookup
        for pos_tag, word_list in self.pos_dictionary.items():
            if word_lower in word_list:
                return pos_tag.upper()
        
        # If not in dictionary, use suffix rules
        pos_from_suffix = self._tag_by_suffix(word_lower)
        if pos_from_suffix:
            return pos_from_suffix.upper()
        
        # Default heuristics
        return self._default_tag(word)
    
    def _tag_by_suffix(self, word: str) -> str:
        """
        Tag word based on suffix rules
        
        Args:
            word (str): Word to analyze
            
        Returns:
            str: POS tag or None
        """
        # Check suffixes in order of length (longest first)
        sorted_suffixes = sorted(self.suffix_rules.items(), 
                               key=lambda x: len(x[0]), reverse=True)
        
        for suffix, pos_tag in sorted_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix):
                return pos_tag
        
        return None
    
    def _default_tag(self, word: str) -> str:
        """
        Apply default tagging heuristics
        
        Args:
            word (str): Word to tag
            
        Returns:
            str: POS tag
        """
        # Capitalized words (except sentence start) might be proper nouns
        if word[0].isupper() and len(word) > 1:
            return 'NOUN'
        
        # Numbers
        if word.isdigit():
            return 'NUMBER'
        
        # Words with digits might be identifiers
        if any(c.isdigit() for c in word):
            return 'IDENTIFIER'
        
        # Punctuation
        if not word.isalnum():
            return 'PUNCTUATION'
        
        # Default to noun for unknown words
        return 'NOUN'
    
    def tag_tokens(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """
        Tag a list of tokens
        
        Args:
            tokens (List[str]): List of tokens to tag
            
        Returns:
            List[Tuple[str, str]]: List of (token, tag) pairs
        """
        tagged_tokens = []
        
        for i, token in enumerate(tokens):
            tag = self.tag_word(token)
            
            # Apply contextual rules
            tag = self._apply_contextual_rules(token, tag, tokens, i)
            
            tagged_tokens.append((token, tag))
        
        return tagged_tokens
    
    def _apply_contextual_rules(self, token: str, tag: str, tokens: List[str], 
                              position: int) -> str:
        """
        Apply contextual rules to improve tagging accuracy
        
        Args:
            token (str): Current token
            tag (str): Current tag
            tokens (List[str]): All tokens
            position (int): Position of current token
            
        Returns:
            str: Refined POS tag
        """
        # Rule: Words after determiners are likely nouns
        if position > 0:
            prev_token = tokens[position - 1].lower()
            if prev_token in ['the', 'a', 'an', 'this', 'that', 'these', 'those']:
                if tag in ['UNKNOWN', 'NOUN']:
                    return 'NOUN'
        
        # Rule: Words ending in -ly after verbs/adjectives are adverbs
        if token.lower().endswith('ly') and position > 0:
            prev_tag = self.tag_word(tokens[position - 1])
            if prev_tag in ['VERB', 'ADJECTIVE']:
                return 'ADVERB'
        
        # Rule: First word of sentence starting with capital might be proper noun
        if position == 0 and token[0].isupper() and len(token) > 1:
            if tag == 'NOUN':
                return 'PROPER_NOUN'
        
        return tag
    
    def get_pos_stats(self, tagged_tokens: List[Tuple[str, str]]) -> Dict[str, int]:
        """
        Get statistics about POS tags in tagged tokens
        
        Args:
            tagged_tokens (List[Tuple[str, str]]): Tagged tokens
            
        Returns:
            Dict[str, int]: Count of each POS tag
        """
        stats = {}
        for token, tag in tagged_tokens:
            stats[tag] = stats.get(tag, 0) + 1
        return stats
