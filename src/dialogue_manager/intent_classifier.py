"""
Rule-based intent classification using pattern matching
"""
import re
from typing import Dict, List, Tuple


class IntentClassifier:
    """
    Rule-based intent classifier using pattern matching
    """
    
    def __init__(self):
        # Define intent patterns (regex patterns and keywords)
        self.intent_patterns = {
            'greeting': {
                'patterns': [
                    r'\b(hello|hi|hey|greetings|good\s+(morning|afternoon|evening))\b',
                    r'\b(howdy|what\'s\s+up|sup)\b'
                ],
                'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 
                           'good evening', 'howdy', "what's up", 'sup'],
                'priority': 1
            },
            'goodbye': {
                'patterns': [
                    r'\b(goodbye|bye|see\s+you|farewell|take\s+care)\b',
                    r'\b(good\s+night|talk\s+to\s+you\s+later|ttyl)\b'
                ],
                'keywords': ['goodbye', 'bye', 'see you', 'farewell', 'take care', 
                           'good night', 'talk to you later', 'ttyl'],
                'priority': 1
            },
            'question': {
                'patterns': [
                    r'^\s*(what|who|when|where|why|how|which|whose)\b',
                    r'\b(can\s+you|could\s+you|would\s+you|will\s+you)\b.*\?',
                    r'\b(is|are|was|were|do|does|did|have|has|had)\b.*\?'
                ],
                'keywords': ['what', 'who', 'when', 'where', 'why', 'how', 'which', 'whose',
                           'can you', 'could you', 'would you', 'will you'],
                'priority': 2
            },
            'request': {
                'patterns': [
                    r'\b(please|can\s+you|could\s+you|would\s+you)\b',
                    r'\b(help\s+me|assist\s+me|show\s+me|tell\s+me)\b',
                    r'\b(i\s+need|i\s+want|i\s+would\s+like)\b'
                ],
                'keywords': ['please', 'can you', 'could you', 'would you', 'help me', 
                           'assist me', 'show me', 'tell me', 'i need', 'i want', 'i would like'],
                'priority': 2
            },
            'compliment': {
                'patterns': [
                    r'\b(you\s+are|you\'re)\s+(great|amazing|awesome|wonderful|fantastic|brilliant)\b',
                    r'\b(good\s+job|well\s+done|excellent|perfect|outstanding)\b',
                    r'\b(i\s+love|i\s+like)\s+(you|this|that)\b'
                ],
                'keywords': ['great', 'amazing', 'awesome', 'wonderful', 'fantastic', 'brilliant',
                           'good job', 'well done', 'excellent', 'perfect', 'outstanding'],
                'priority': 2
            },
            'complaint': {
                'patterns': [
                    r'\b(this\s+is|that\s+is|you\s+are)\s+(bad|terrible|awful|horrible|wrong)\b',
                    r'\b(i\s+hate|i\s+dislike|i\s+don\'t\s+like)\b',
                    r'\b(problem|issue|trouble|error|mistake)\b'
                ],
                'keywords': ['bad', 'terrible', 'awful', 'horrible', 'wrong', 'hate', 'dislike',
                           "don't like", 'problem', 'issue', 'trouble', 'error', 'mistake'],
                'priority': 2
            },
            'information': {
                'patterns': [
                    r'\b(tell\s+me\s+about|what\s+is|what\s+are)\b',
                    r'\b(explain|describe|define)\b',
                    r'\b(information\s+about|details\s+about)\b'
                ],
                'keywords': ['tell me about', 'what is', 'what are', 'explain', 'describe', 
                           'define', 'information about', 'details about'],
                'priority': 2
            },
            'affirmation': {
                'patterns': [
                    r'\b(yes|yeah|yep|yup|sure|okay|ok|alright|right)\b',
                    r'\b(absolutely|definitely|certainly|of\s+course)\b'
                ],
                'keywords': ['yes', 'yeah', 'yep', 'yup', 'sure', 'okay', 'ok', 'alright', 
                           'right', 'absolutely', 'definitely', 'certainly', 'of course'],
                'priority': 1
            },
            'negation': {
                'patterns': [
                    r'\b(no|nope|nah|not\s+really|i\s+don\'t\s+think\s+so)\b',
                    r'\b(never|nothing|nobody|nowhere)\b'
                ],
                'keywords': ['no', 'nope', 'nah', 'not really', "i don't think so", 
                           'never', 'nothing', 'nobody', 'nowhere'],
                'priority': 1
            },
            'personal_info': {
                'patterns': [
                    r'\b(my\s+name\s+is|i\s+am|i\'m|call\s+me)\b',
                    r'\b(i\s+live\s+in|i\s+work\s+at|i\s+study\s+at)\b',
                    r'\b(i\s+like|i\s+love|i\s+enjoy|i\s+prefer)\b'
                ],
                'keywords': ['my name is', 'i am', "i'm", 'call me', 'i live in', 
                           'i work at', 'i study at', 'i like', 'i love', 'i enjoy', 'i prefer'],
                'priority': 2
            }
        }
    
    def classify_intent(self, text: str, tokens: List[str] = None) -> Tuple[str, float]:
        """
        Classify the intent of input text
        
        Args:
            text (str): Input text to classify
            tokens (List[str]): Optional pre-tokenized text
            
        Returns:
            Tuple[str, float]: (intent, confidence_score)
        """
        if not text.strip():
            return 'unknown', 0.0
        
        text_lower = text.lower()
        intent_scores = {}
        
        # Check each intent pattern
        for intent, config in self.intent_patterns.items():
            score = self._calculate_intent_score(text_lower, config)
            if score > 0:
                intent_scores[intent] = score
        
        # If no patterns matched, return default
        if not intent_scores:
            return self._get_default_intent(text_lower), 0.3
        
        # Return intent with highest score
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], min(best_intent[1], 1.0)
    
    def _calculate_intent_score(self, text: str, config: Dict) -> float:
        """
        Calculate score for a specific intent
        
        Args:
            text (str): Input text (lowercase)
            config (Dict): Intent configuration
            
        Returns:
            float: Intent score
        """
        score = 0.0
        
        # Check regex patterns
        for pattern in config.get('patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.5 * config.get('priority', 1)
        
        # Check keywords
        for keyword in config.get('keywords', []):
            if keyword.lower() in text:
                score += 0.3 * config.get('priority', 1)
        
        return score
    
    def _get_default_intent(self, text: str) -> str:
        """
        Determine default intent based on simple heuristics
        
        Args:
            text (str): Input text (lowercase)
            
        Returns:
            str: Default intent
        """
        # Check for question markers
        if '?' in text or text.startswith(('what', 'who', 'when', 'where', 'why', 'how')):
            return 'question'
        
        # Check for imperative mood (commands/requests)
        if any(text.startswith(word) for word in ['please', 'help', 'show', 'tell', 'give']):
            return 'request'
        
        # Check for emotional expressions
        if any(word in text for word in ['love', 'like', 'happy', 'excited']):
            return 'positive_emotion'
        
        if any(word in text for word in ['sad', 'angry', 'frustrated', 'upset']):
            return 'negative_emotion'
        
        # Default to statement/information
        return 'statement'
    
    def get_intent_confidence_threshold(self, intent: str) -> float:
        """
        Get confidence threshold for a specific intent
        
        Args:
            intent (str): Intent name
            
        Returns:
            float: Confidence threshold
        """
        thresholds = {
            'greeting': 0.5,
            'goodbye': 0.5,
            'question': 0.4,
            'request': 0.4,
            'compliment': 0.6,
            'complaint': 0.6,
            'affirmation': 0.5,
            'negation': 0.5,
            'personal_info': 0.5,
            'information': 0.4
        }
        
        return thresholds.get(intent, 0.3)
    
    def classify_with_context(self, text: str, previous_intents: List[str] = None,
                            conversation_state: Dict = None) -> Tuple[str, float]:
        """
        Classify intent with conversation context
        
        Args:
            text (str): Input text
            previous_intents (List[str]): Previous conversation intents
            conversation_state (Dict): Current conversation state
            
        Returns:
            Tuple[str, float]: (intent, confidence_score)
        """
        intent, confidence = self.classify_intent(text)
        
        # Adjust confidence based on context
        if previous_intents:
            # Boost confidence for follow-up patterns
            last_intent = previous_intents[-1] if previous_intents else None
            
            if last_intent == 'question' and intent in ['affirmation', 'negation', 'information']:
                confidence += 0.2
            
            if last_intent == 'greeting' and intent == 'personal_info':
                confidence += 0.1
            
            if last_intent == 'request' and intent in ['affirmation', 'negation']:
                confidence += 0.2
        
        return intent, min(confidence, 1.0)
    
    def get_supported_intents(self) -> List[str]:
        """Get list of all supported intents"""
        return list(self.intent_patterns.keys())
    
    def add_custom_intent(self, intent_name: str, patterns: List[str], 
                         keywords: List[str], priority: int = 1) -> None:
        """
        Add a custom intent pattern
        
        Args:
            intent_name (str): Name of the new intent
            patterns (List[str]): Regex patterns for the intent
            keywords (List[str]): Keywords for the intent
            priority (int): Priority weight for the intent
        """
        self.intent_patterns[intent_name] = {
            'patterns': patterns,
            'keywords': keywords,
            'priority': priority
        }
