"""
Lexicon-based sentiment analysis
"""
import json
import os
from typing import List, Dict, Tuple


class SentimentAnalyzer:
    """
    Lexicon-based sentiment analyzer
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data directory relative to this file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(current_dir, 'data')
        
        self.data_dir = data_dir
        self.lexicon = self._load_lexicon()
        
        # Sentiment modifiers
        self.intensifiers = ['very', 'really', 'extremely', 'incredibly', 'absolutely', 'quite']
        self.negators = ['not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere']
        self.diminishers = ['slightly', 'somewhat', 'rather', 'fairly', 'pretty', 'kind of', 'sort of']
    
    def _load_lexicon(self) -> Dict[str, List[str]]:
        """Load sentiment lexicon from JSON file"""
        try:
            lexicon_path = os.path.join(self.data_dir, 'lexicon.json')
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'positive': [], 'negative': [], 'neutral': []}
    
    def analyze_sentiment(self, tokens: List[str]) -> Dict[str, float]:
        """
        Analyze sentiment of a list of tokens
        
        Args:
            tokens (List[str]): List of tokens to analyze
            
        Returns:
            Dict[str, float]: Sentiment scores and classification
        """
        if not tokens:
            return {
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 0.0,
                'compound_score': 0.0,
                'sentiment': 'neutral'
            }
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Process tokens with context
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Get base sentiment
            base_sentiment = self._get_token_sentiment(token_lower)
            if base_sentiment == 'neutral':
                neutral_count += 1
                continue
            
            # Apply modifiers
            sentiment_strength = self._apply_modifiers(tokens, i, base_sentiment)
            
            if base_sentiment == 'positive':
                positive_count += sentiment_strength
            elif base_sentiment == 'negative':
                negative_count += sentiment_strength
        
        # Calculate scores
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return {
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 1.0,
                'compound_score': 0.0,
                'sentiment': 'neutral'
            }
        
        positive_score = positive_count / len(tokens)
        negative_score = negative_count / len(tokens)
        neutral_score = neutral_count / len(tokens)
        
        # Compound score: normalized between -1 and 1
        compound_score = (positive_count - negative_count) / len(tokens)
        
        # Determine overall sentiment
        if compound_score >= 0.05:
            sentiment = 'positive'
        elif compound_score <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'positive_score': positive_score,
            'negative_score': negative_score,
            'neutral_score': neutral_score,
            'compound_score': compound_score,
            'sentiment': sentiment
        }
    
    def _get_token_sentiment(self, token: str) -> str:
        """
        Get sentiment category for a single token
        
        Args:
            token (str): Token to analyze
            
        Returns:
            str: 'positive', 'negative', or 'neutral'
        """
        if token in self.lexicon.get('positive', []):
            return 'positive'
        elif token in self.lexicon.get('negative', []):
            return 'negative'
        else:
            return 'neutral'
    
    def _apply_modifiers(self, tokens: List[str], position: int, base_sentiment: str) -> float:
        """
        Apply sentiment modifiers based on context
        
        Args:
            tokens (List[str]): All tokens
            position (int): Position of current token
            base_sentiment (str): Base sentiment of token
            
        Returns:
            float: Modified sentiment strength
        """
        strength = 1.0
        
        # Check previous tokens for modifiers
        window_start = max(0, position - 3)
        context_tokens = [t.lower() for t in tokens[window_start:position]]
        
        # Apply negation
        if any(negator in context_tokens for negator in self.negators):
            # Flip sentiment and reduce strength
            return 0.5 if base_sentiment == 'positive' else -0.5
        
        # Apply intensifiers
        if any(intensifier in context_tokens for intensifier in self.intensifiers):
            strength *= 1.5
        
        # Apply diminishers
        if any(diminisher in context_tokens for diminisher in self.diminishers):
            strength *= 0.5
        
        return strength
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of raw text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: Sentiment analysis results
        """
        # Simple tokenization for this method
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return self.analyze_sentiment(tokens)
    
    def get_sentiment_words(self, tokens: List[str]) -> Dict[str, List[str]]:
        """
        Extract sentiment-bearing words from tokens
        
        Args:
            tokens (List[str]): List of tokens
            
        Returns:
            Dict[str, List[str]]: Categorized sentiment words
        """
        sentiment_words = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        for token in tokens:
            token_lower = token.lower()
            sentiment = self._get_token_sentiment(token_lower)
            sentiment_words[sentiment].append(token)
        
        return sentiment_words
