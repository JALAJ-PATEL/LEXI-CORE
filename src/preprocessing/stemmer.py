"""
Rule-based stemming implementation
"""
import re
from typing import List


class Stemmer:
    """
    Rule-based stemmer for reducing words to their root forms
    """
    
    def __init__(self):
        # Define stemming rules (suffix -> replacement)
        self.stemming_rules = {
            # Plural rules
            'ies': 'y',     # flies -> fly
            'ied': 'y',     # tried -> try
            'ying': 'y',    # flying -> fly
            'ies': 'y',     # flies -> fly
            'ses': 's',     # passes -> pass
            'xes': 'x',     # fixes -> fix
            'zes': 'z',     # prizes -> prize
            'ches': 'ch',   # watches -> watch
            'shes': 'sh',   # wishes -> wish
            's': '',        # cats -> cat (general plural)
            
            # Past tense rules
            'ied': 'y',     # tried -> try
            'ed': '',       # walked -> walk
            
            # Present participle / gerund rules
            'ing': '',      # walking -> walk
            
            # Comparative and superlative
            'ier': 'y',     # happier -> happy
            'iest': 'y',    # happiest -> happy
            'er': '',       # bigger -> big
            'est': '',      # biggest -> big
            
            # Adverb rules
            'ly': '',       # quickly -> quick
            
            # Other common suffixes
            'tion': 't',    # action -> act
            'sion': 's',    # decision -> decis
            'ment': '',     # movement -> move
            'ness': '',     # happiness -> happy
            'ity': '',      # activity -> activ
            'able': '',     # readable -> read
            'ible': '',     # visible -> vis
        }
        
        # Exceptions that should not be stemmed
        self.exceptions = {
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having',
            'do', 'does', 'did', 'doing',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else',
            'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their'
        }
    
    def stem(self, word: str) -> str:
        """
        Stem a single word
        
        Args:
            word (str): Word to stem
            
        Returns:
            str: Stemmed word
        """
        if not word:
            return word
        
        word = word.lower()
        
        # Don't stem very short words or exceptions
        if len(word) <= 2 or word in self.exceptions:
            return word
        
        original_word = word
        
        # Apply stemming rules in order of priority (longest suffixes first)
        sorted_rules = sorted(self.stemming_rules.items(), 
                            key=lambda x: len(x[0]), reverse=True)
        
        for suffix, replacement in sorted_rules:
            if word.endswith(suffix):
                # Check if removing suffix would leave a reasonable root
                root = word[:-len(suffix)] + replacement
                if len(root) >= 2:  # Ensure root is at least 2 characters
                    return root
        
        return original_word
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """
        Stem a list of tokens
        
        Args:
            tokens (List[str]): List of tokens to stem
            
        Returns:
            List[str]: List of stemmed tokens
        """
        return [self.stem(token) for token in tokens]
    
    def _is_vowel(self, char: str) -> bool:
        """Check if character is a vowel"""
        return char.lower() in 'aeiou'
    
    def _consonant_vowel_pattern(self, word: str) -> str:
        """
        Generate consonant-vowel pattern for word
        Useful for more advanced stemming rules
        """
        pattern = ""
        for char in word:
            if char.isalpha():
                pattern += 'V' if self._is_vowel(char) else 'C'
        return pattern
