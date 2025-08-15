"""
Dynamic response generation using templates, POS tags, and entities
"""
import json
import os
import random
from typing import Dict, List, Any, Optional


class ResponseGenerator:
    """
    Generates dynamic responses using templates, entities, and conversation context
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to data directory relative to this file
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            data_dir = os.path.join(current_dir, 'data')
        
        self.data_dir = data_dir
        self.response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates from JSON file"""
        try:
            templates_path = os.path.join(self.data_dir, 'response_templates.json')
            with open(templates_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, List[str]]:
        """Get default response templates if file loading fails"""
        return {
            'greeting': ["Hello! How can I help you today?"],
            'goodbye': ["Goodbye! It was nice talking with you."],
            'question': ["That's an interesting question. Let me think about that."],
            'compliment': ["Thank you! That's very kind of you to say."],
            'complaint': ["I understand your concern. Let me see how I can help."],
            'request': ["I'd be happy to help you with that."],
            'information': ["Here's what I can tell you about that:"],
            'default': ["I see. Can you tell me more about that?"]
        }
    
    def generate_response(self, intent: str, entities: Dict[str, List[Any]], 
                         sentiment: Dict[str, float], user_input: str,
                         conversation_state: Dict = None) -> str:
        """
        Generate a response based on intent, entities, sentiment, and context
        
        Args:
            intent (str): Classified intent
            entities (Dict[str, List[Any]]): Extracted entities
            sentiment (Dict[str, float]): Sentiment analysis results
            user_input (str): Original user input
            conversation_state (Dict): Current conversation state
            
        Returns:
            str: Generated response
        """
        # Get base template
        template = self._select_template(intent, sentiment)
        
        # Fill in template placeholders
        response = self._fill_template(template, entities, conversation_state, user_input)
        
        # Apply sentiment-based modifications
        response = self._apply_sentiment_modifications(response, sentiment)
        
        # Apply personalization if user info available
        response = self._apply_personalization(response, conversation_state)
        
        return response
    
    def _select_template(self, intent: str, sentiment: Dict[str, float]) -> str:
        """
        Select appropriate template based on intent and sentiment
        
        Args:
            intent (str): Classified intent
            sentiment (Dict[str, float]): Sentiment analysis
            
        Returns:
            str: Selected template
        """
        # Map intent to template category
        template_category = self._map_intent_to_template_category(intent)
        
        # Get templates for this category
        templates = self.response_templates.get(template_category, 
                                              self.response_templates.get('default', 
                                                                        ['I understand.']))
        
        # Select template based on sentiment if multiple available
        if len(templates) > 1:
            sentiment_label = sentiment.get('sentiment', 'neutral')
            
            # Simple selection based on sentiment
            if sentiment_label == 'positive':
                # Choose more enthusiastic templates (later in list)
                index = min(len(templates) - 1, random.randint(len(templates)//2, len(templates) - 1))
            elif sentiment_label == 'negative':
                # Choose more empathetic templates (earlier in list)
                index = random.randint(0, len(templates)//2)
            else:
                # Random selection for neutral
                index = random.randint(0, len(templates) - 1)
            
            return templates[index]
        
        return templates[0] if templates else "I understand."
    
    def _map_intent_to_template_category(self, intent: str) -> str:
        """Map intent to response template category"""
        intent_mapping = {
            'greeting': 'greeting',
            'goodbye': 'goodbye',
            'question': 'question',
            'compliment': 'compliment',
            'complaint': 'complaint',
            'request': 'request',
            'information': 'information',
            'affirmation': 'default',
            'negation': 'default',
            'personal_info': 'default',
            'statement': 'default'
        }
        
        return intent_mapping.get(intent, 'default')
    
    def _fill_template(self, template: str, entities: Dict[str, List[Any]], 
                      conversation_state: Dict, user_input: str) -> str:
        """
        Fill template placeholders with dynamic content
        
        Args:
            template (str): Template string
            entities (Dict[str, List[Any]]): Extracted entities
            conversation_state (Dict): Conversation context
            user_input (str): User's input
            
        Returns:
            str: Filled template
        """
        response = template
        
        # Fill {topic} placeholder
        topic = self._extract_topic(entities, user_input, conversation_state)
        response = response.replace('{topic}', topic)
        
        # Fill {name} placeholder
        user_name = self._get_user_name(conversation_state)
        if user_name and '{name}' in response:
            response = response.replace('{name}', user_name)
        
        # Fill {entity} placeholders for specific entity types
        for entity_type, entity_list in entities.items():
            placeholder = f'{{{entity_type.lower()}}}'
            if placeholder in response and entity_list:
                entity_text = entity_list[0].get('text', str(entity_list[0]))
                response = response.replace(placeholder, entity_text)
        
        return response
    
    def _extract_topic(self, entities: Dict[str, List[Any]], user_input: str,
                      conversation_state: Dict) -> str:
        """
        Extract main topic from entities and input
        
        Args:
            entities (Dict[str, List[Any]]): Extracted entities
            user_input (str): User input
            conversation_state (Dict): Conversation state
            
        Returns:
            str: Main topic or generic placeholder
        """
        # Priority order for entity types as topics
        priority_entities = ['ORGANIZATION', 'LOCATION', 'PERSON', 'TIME']
        
        for entity_type in priority_entities:
            if entity_type in entities and entities[entity_type]:
                return entities[entity_type][0].get('text', str(entities[entity_type][0]))
        
        # If no priority entities, look for any entities
        for entity_list in entities.values():
            if entity_list:
                return entity_list[0].get('text', str(entity_list[0]))
        
        # Fall back to extracting key nouns from user input
        key_words = self._extract_key_words(user_input)
        if key_words:
            return key_words[0]
        
        # Default topic
        return "that"
    
    def _extract_key_words(self, text: str) -> List[str]:
        """
        Extract key words from text (simple implementation)
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: Key words
        """
        import re
        
        # Remove common stop words and extract meaningful words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_words[:3]  # Return top 3 key words
    
    def _get_user_name(self, conversation_state: Dict) -> Optional[str]:
        """Get user name from conversation state"""
        if conversation_state and hasattr(conversation_state, 'get_user_name'):
            return conversation_state.get_user_name()
        return None
    
    def _apply_sentiment_modifications(self, response: str, sentiment: Dict[str, float]) -> str:
        """
        Modify response based on user sentiment
        
        Args:
            response (str): Base response
            sentiment (Dict[str, float]): Sentiment analysis
            
        Returns:
            str: Modified response
        """
        sentiment_label = sentiment.get('sentiment', 'neutral')
        compound_score = sentiment.get('compound_score', 0.0)
        
        # Add sentiment-appropriate modifiers
        if sentiment_label == 'negative' and compound_score < -0.5:
            # Strong negative sentiment - add empathy
            empathy_phrases = [
                "I can understand that must be frustrating. ",
                "I hear that you're upset about this. ",
                "That sounds really difficult. "
            ]
            response = random.choice(empathy_phrases) + response
        
        elif sentiment_label == 'positive' and compound_score > 0.5:
            # Strong positive sentiment - add enthusiasm
            enthusiasm_phrases = [
                "That's wonderful! ",
                "How exciting! ",
                "That's fantastic! "
            ]
            response = random.choice(enthusiasm_phrases) + response
        
        return response
    
    def _apply_personalization(self, response: str, conversation_state: Dict) -> str:
        """
        Apply personalization based on conversation history
        
        Args:
            response (str): Base response
            conversation_state (Dict): Conversation state
            
        Returns:
            str: Personalized response
        """
        if not conversation_state:
            return response
        
        # Add user name if available and appropriate
        user_name = self._get_user_name(conversation_state)
        if user_name and random.random() < 0.3:  # 30% chance to use name
            response = f"{user_name}, {response.lower()}"
        
        # Reference user preferences if relevant
        if hasattr(conversation_state, 'get_user_preferences'):
            preferences = conversation_state.get_user_preferences()
            if preferences and any(pref in response.lower() for pref in preferences):
                response += " I remember you mentioned you like that!"
        
        return response
    
    def generate_follow_up_question(self, intent: str, entities: Dict[str, List[Any]],
                                  topic: str = None) -> str:
        """
        Generate a follow-up question to keep conversation flowing
        
        Args:
            intent (str): Current intent
            entities (Dict[str, List[Any]]): Extracted entities
            topic (str): Current topic
            
        Returns:
            str: Follow-up question
        """
        follow_up_templates = {
            'information': [
                "Would you like to know more about {topic}?",
                "Is there anything specific about {topic} you'd like to explore?",
                "What else would you like to know?"
            ],
            'personal_info': [
                "That's interesting! Tell me more about that.",
                "How long have you been interested in that?",
                "What got you started with that?"
            ],
            'question': [
                "Does that help answer your question?",
                "Is there anything else you'd like to know?",
                "What other questions do you have?"
            ],
            'default': [
                "What would you like to talk about next?",
                "Is there anything else I can help you with?",
                "What's on your mind?"
            ]
        }
        
        templates = follow_up_templates.get(intent, follow_up_templates['default'])
        template = random.choice(templates)
        
        if topic and '{topic}' in template:
            template = template.replace('{topic}', topic)
        
        return template
