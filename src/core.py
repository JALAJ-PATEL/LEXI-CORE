"""
Core NLP pipeline that orchestrates all components
"""
import os
from typing import Dict, List, Any, Tuple

# Import all components
from .preprocessing.tokenizer import Tokenizer
from .preprocessing.normalizer import Normalizer
from .preprocessing.stemmer import Stemmer
from .linguistic_analysis.pos_tagger import POSTagger
from .linguistic_analysis.sentiment_analyzer import SentimentAnalyzer
from .linguistic_analysis.entity_extractor import EntityExtractor
from .dialogue_manager.state_tracker import StateTracker
from .dialogue_manager.intent_classifier import IntentClassifier
from .dialogue_manager.response_generator import ResponseGenerator


class LexiCore:
    """
    Main NLP pipeline that coordinates all processing components
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the LexiCore pipeline
        
        Args:
            data_dir (str): Path to data directory containing JSON files
        """
        if data_dir is None:
            # Default to data directory relative to this file
            current_dir = os.path.dirname(__file__)
            data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        
        self.data_dir = data_dir
        
        # Initialize preprocessing components
        self.tokenizer = Tokenizer()
        self.normalizer = Normalizer(data_dir)
        self.stemmer = Stemmer()
        
        # Initialize linguistic analysis components
        self.pos_tagger = POSTagger(data_dir)
        self.sentiment_analyzer = SentimentAnalyzer(data_dir)
        self.entity_extractor = EntityExtractor()
        
        # Initialize dialogue management components
        self.state_tracker = StateTracker()
        self.intent_classifier = IntentClassifier()
        self.response_generator = ResponseGenerator(data_dir)
        
        # Processing options
        self.options = {
            'apply_stemming': True,
            'extract_entities': True,
            'track_sentiment': True,
            'generate_response': True
        }
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the complete NLP pipeline
        
        Args:
            user_input (str): Raw user input text
            
        Returns:
            Dict[str, Any]: Complete analysis results
        """
        if not user_input or not user_input.strip():
            return self._get_empty_result()
        
        # Step 1: Preprocessing
        preprocessing_results = self._preprocess_text(user_input)
        
        # Step 2: Linguistic Analysis
        linguistic_results = self._analyze_linguistics(
            preprocessing_results['normalized_text'],
            preprocessing_results['tokens']
        )
        
        # Step 3: Dialogue Management
        dialogue_results = self._manage_dialogue(
            user_input,
            preprocessing_results,
            linguistic_results
        )
        
        # Step 4: Combine all results
        complete_results = {
            'input': user_input,
            'preprocessing': preprocessing_results,
            'linguistic_analysis': linguistic_results,
            'dialogue_management': dialogue_results,
            'response': dialogue_results.get('response', '')
        }
        
        # Step 5: Update conversation state
        self._update_conversation_state(complete_results)
        
        return complete_results
    
    def _preprocess_text(self, text: str) -> Dict[str, Any]:
        """
        Apply preprocessing steps to input text
        
        Args:
            text (str): Raw input text
            
        Returns:
            Dict[str, Any]: Preprocessing results
        """
        # Tokenization
        tokens = self.tokenizer.tokenize(text)
        
        # Normalization
        normalized_text = self.normalizer.normalize_text(text)
        normalized_tokens = self.normalizer.normalize_tokens(tokens)
        
        # Stemming (optional)
        stemmed_tokens = []
        if self.options['apply_stemming']:
            stemmed_tokens = self.stemmer.stem_tokens(normalized_tokens)
        
        return {
            'original_text': text,
            'normalized_text': normalized_text,
            'tokens': tokens,
            'normalized_tokens': normalized_tokens,
            'stemmed_tokens': stemmed_tokens,
            'token_count': len(tokens)
        }
    
    def _analyze_linguistics(self, text: str, tokens: List[str]) -> Dict[str, Any]:
        """
        Perform linguistic analysis on preprocessed text
        
        Args:
            text (str): Normalized text
            tokens (List[str]): Tokenized text
            
        Returns:
            Dict[str, Any]: Linguistic analysis results
        """
        results = {}
        
        # POS Tagging
        pos_tagged = self.pos_tagger.tag_tokens(tokens)
        results['pos_tags'] = pos_tagged
        results['pos_stats'] = self.pos_tagger.get_pos_stats(pos_tagged)
        
        # Sentiment Analysis
        if self.options['track_sentiment']:
            sentiment = self.sentiment_analyzer.analyze_sentiment(tokens)
            sentiment_words = self.sentiment_analyzer.get_sentiment_words(tokens)
            results['sentiment'] = sentiment
            results['sentiment_words'] = sentiment_words
        
        # Entity Extraction
        if self.options['extract_entities']:
            entities = self.entity_extractor.extract_entities(tokens, pos_tagged)
            results['entities'] = entities
            results['entity_count'] = sum(len(entity_list) for entity_list in entities.values())
        
        return results
    
    def _manage_dialogue(self, user_input: str, preprocessing: Dict[str, Any],
                        linguistic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle dialogue management tasks
        
        Args:
            user_input (str): Original user input
            preprocessing (Dict[str, Any]): Preprocessing results
            linguistic (Dict[str, Any]): Linguistic analysis results
            
        Returns:
            Dict[str, Any]: Dialogue management results
        """
        results = {}
        
        # Intent Classification
        intent, intent_confidence = self.intent_classifier.classify_intent(
            user_input, 
            preprocessing['tokens']
        )
        results['intent'] = intent
        results['intent_confidence'] = intent_confidence
        
        # Extract data for response generation
        entities = linguistic.get('entities', {})
        sentiment = linguistic.get('sentiment', {'sentiment': 'neutral', 'compound_score': 0.0})
        
        # Generate Response
        if self.options['generate_response']:
            response = self.response_generator.generate_response(
                intent=intent,
                entities=entities,
                sentiment=sentiment,
                user_input=user_input,
                conversation_state=self.state_tracker
            )
            results['response'] = response
            
            # Generate follow-up question if appropriate
            topic = self._extract_main_topic(entities, user_input)
            follow_up = self.response_generator.generate_follow_up_question(
                intent, entities, topic
            )
            results['follow_up_question'] = follow_up
        
        return results
    
    def _update_conversation_state(self, results: Dict[str, Any]) -> None:
        """
        Update conversation state with latest turn
        
        Args:
            results (Dict[str, Any]): Complete processing results
        """
        user_input = results['input']
        bot_response = results.get('response', '')
        sentiment = results['linguistic_analysis'].get('sentiment', {})
        entities = results['linguistic_analysis'].get('entities', {})
        intent = results['dialogue_management'].get('intent', 'unknown')
        pos_tags = results['linguistic_analysis'].get('pos_tags', [])
        
        self.state_tracker.update_turn(
            user_input=user_input,
            bot_response=bot_response,
            sentiment=sentiment,
            entities=entities,
            intent=intent,
            pos_tags=pos_tags
        )
    
    def _extract_main_topic(self, entities: Dict[str, List[Any]], user_input: str) -> str:
        """
        Extract main topic from entities and input
        
        Args:
            entities (Dict[str, List[Any]]): Extracted entities
            user_input (str): User input
            
        Returns:
            str: Main topic
        """
        # Priority order for entities as topics
        priority_entities = ['ORGANIZATION', 'LOCATION', 'PERSON']
        
        for entity_type in priority_entities:
            if entity_type in entities and entities[entity_type]:
                return entities[entity_type][0].get('text', str(entities[entity_type][0]))
        
        # Fall back to any entity
        for entity_list in entities.values():
            if entity_list:
                return entity_list[0].get('text', str(entity_list[0]))
        
        return "that"
    
    def _get_empty_result(self) -> Dict[str, Any]:
        """Get empty result structure for invalid input"""
        return {
            'input': '',
            'preprocessing': {
                'original_text': '',
                'normalized_text': '',
                'tokens': [],
                'normalized_tokens': [],
                'stemmed_tokens': [],
                'token_count': 0
            },
            'linguistic_analysis': {
                'pos_tags': [],
                'pos_stats': {},
                'sentiment': {'sentiment': 'neutral', 'compound_score': 0.0},
                'sentiment_words': {'positive': [], 'negative': [], 'neutral': []},
                'entities': {},
                'entity_count': 0
            },
            'dialogue_management': {
                'intent': 'unknown',
                'intent_confidence': 0.0,
                'response': "I didn't understand that. Could you please say something?",
                'follow_up_question': "What would you like to talk about?"
            },
            'response': "I didn't understand that. Could you please say something?"
        }
    
    def get_conversation_state(self) -> StateTracker:
        """Get current conversation state"""
        return self.state_tracker
    
    def reset_conversation(self) -> None:
        """Reset conversation state"""
        self.state_tracker.reset_conversation()
    
    def set_processing_options(self, **options) -> None:
        """
        Set processing options
        
        Args:
            **options: Processing options to update
        """
        self.options.update(options)
    
    def get_processing_options(self) -> Dict[str, bool]:
        """Get current processing options"""
        return self.options.copy()
    
    def analyze_text_only(self, text: str) -> Dict[str, Any]:
        """
        Analyze text without dialogue management (for batch processing)
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, Any]: Analysis results without response generation
        """
        # Temporarily disable response generation
        original_generate_response = self.options['generate_response']
        self.options['generate_response'] = False
        
        try:
            # Process without updating conversation state
            preprocessing_results = self._preprocess_text(text)
            linguistic_results = self._analyze_linguistics(
                preprocessing_results['normalized_text'],
                preprocessing_results['tokens']
            )
            
            # Basic intent classification without dialogue context
            intent, intent_confidence = self.intent_classifier.classify_intent(
                text, preprocessing_results['tokens']
            )
            
            return {
                'input': text,
                'preprocessing': preprocessing_results,
                'linguistic_analysis': linguistic_results,
                'intent': intent,
                'intent_confidence': intent_confidence
            }
        
        finally:
            # Restore original setting
            self.options['generate_response'] = original_generate_response
