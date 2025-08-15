"""
Conversation state tracker for managing dialogue context
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


class StateTracker:
    """
    Tracks conversation state including user information, sentiment history, and context
    """
    
    def __init__(self):
        self.conversation_history = []
        self.user_info = {}
        self.sentiment_history = []
        self.entities_mentioned = {}
        self.current_topic = None
        self.conversation_start = datetime.now()
        self.turn_count = 0
        self.context_window = 10  # Number of recent turns to keep in active context
    
    def update_turn(self, user_input: str, bot_response: str, 
                   sentiment: Dict[str, float], entities: Dict[str, List],
                   intent: str, pos_tags: List = None) -> None:
        """
        Update state with new conversation turn
        
        Args:
            user_input (str): User's input text
            bot_response (str): Bot's response
            sentiment (Dict[str, float]): Sentiment analysis results
            entities (Dict[str, List]): Extracted entities
            intent (str): Classified intent
            pos_tags (List): POS tags for the input
        """
        self.turn_count += 1
        
        # Add to conversation history
        turn = {
            'turn_id': self.turn_count,
            'timestamp': datetime.now(),
            'user_input': user_input,
            'bot_response': bot_response,
            'sentiment': sentiment,
            'entities': entities,
            'intent': intent,
            'pos_tags': pos_tags
        }
        
        self.conversation_history.append(turn)
        
        # Update sentiment history
        self.sentiment_history.append({
            'turn_id': self.turn_count,
            'sentiment': sentiment['sentiment'],
            'compound_score': sentiment['compound_score']
        })
        
        # Update entities mentioned
        self._update_entities(entities)
        
        # Update user information
        self._update_user_info(entities, user_input)
        
        # Update current topic
        self._update_current_topic(entities, intent)
        
        # Trim history if it gets too long
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-50:]
    
    def _update_entities(self, entities: Dict[str, List]) -> None:
        """Update the entities mentioned in conversation"""
        for entity_type, entity_list in entities.items():
            if entity_type not in self.entities_mentioned:
                self.entities_mentioned[entity_type] = {}
            
            for entity in entity_list:
                entity_text = entity.get('text', str(entity))
                if entity_text in self.entities_mentioned[entity_type]:
                    self.entities_mentioned[entity_type][entity_text] += 1
                else:
                    self.entities_mentioned[entity_type][entity_text] = 1
    
    def _update_user_info(self, entities: Dict[str, List], user_input: str) -> None:
        """Extract and update user information"""
        # Extract user name if mentioned
        if 'PERSON' in entities:
            for person in entities['PERSON']:
                person_text = person.get('text', str(person))
                # Simple heuristic: if user says "I'm [name]" or "My name is [name]"
                if any(phrase in user_input.lower() for phrase in ["i'm ", "my name is", "call me"]):
                    self.user_info['name'] = person_text
                    break
        
        # Extract user preferences (simple keyword matching)
        input_lower = user_input.lower()
        if 'i like' in input_lower or 'i love' in input_lower:
            if 'preferences' not in self.user_info:
                self.user_info['preferences'] = []
            # Extract what comes after "i like" or "i love"
            for phrase in ['i like ', 'i love ']:
                if phrase in input_lower:
                    preference = input_lower.split(phrase, 1)[1].split('.')[0].split(',')[0]
                    if preference not in self.user_info['preferences']:
                        self.user_info['preferences'].append(preference.strip())
        
        # Extract user dislikes
        if 'i hate' in input_lower or 'i dislike' in input_lower:
            if 'dislikes' not in self.user_info:
                self.user_info['dislikes'] = []
            for phrase in ['i hate ', 'i dislike ']:
                if phrase in input_lower:
                    dislike = input_lower.split(phrase, 1)[1].split('.')[0].split(',')[0]
                    if dislike not in self.user_info['dislikes']:
                        self.user_info['dislikes'].append(dislike.strip())
    
    def _update_current_topic(self, entities: Dict[str, List], intent: str) -> None:
        """Update current conversation topic"""
        # Simple topic detection based on entities and intent
        if intent in ['question', 'information']:
            # Look for main entities to determine topic
            for entity_type in ['ORGANIZATION', 'LOCATION', 'PERSON']:
                if entity_type in entities and entities[entity_type]:
                    self.current_topic = entities[entity_type][0].get('text', str(entities[entity_type][0]))
                    break
    
    def get_recent_context(self, num_turns: int = None) -> List[Dict]:
        """
        Get recent conversation context
        
        Args:
            num_turns (int): Number of recent turns to return
            
        Returns:
            List[Dict]: Recent conversation turns
        """
        if num_turns is None:
            num_turns = self.context_window
        
        return self.conversation_history[-num_turns:]
    
    def get_sentiment_trend(self, num_turns: int = 5) -> str:
        """
        Analyze recent sentiment trend
        
        Args:
            num_turns (int): Number of recent turns to analyze
            
        Returns:
            str: Sentiment trend description
        """
        if len(self.sentiment_history) < 2:
            return "neutral"
        
        recent_sentiments = self.sentiment_history[-num_turns:]
        
        if len(recent_sentiments) < 2:
            return recent_sentiments[-1]['sentiment']
        
        # Simple trend analysis
        positive_count = sum(1 for s in recent_sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in recent_sentiments if s['sentiment'] == 'negative')
        
        if positive_count > negative_count:
            return "improving"
        elif negative_count > positive_count:
            return "declining"
        else:
            return "stable"
    
    def get_user_name(self) -> Optional[str]:
        """Get user's name if known"""
        return self.user_info.get('name')
    
    def get_user_preferences(self) -> List[str]:
        """Get user's stated preferences"""
        return self.user_info.get('preferences', [])
    
    def get_user_dislikes(self) -> List[str]:
        """Get user's stated dislikes"""
        return self.user_info.get('dislikes', [])
    
    def get_frequently_mentioned_entities(self, entity_type: str, top_n: int = 3) -> List[str]:
        """
        Get most frequently mentioned entities of a specific type
        
        Args:
            entity_type (str): Type of entity to retrieve
            top_n (int): Number of top entities to return
            
        Returns:
            List[str]: Most frequently mentioned entities
        """
        if entity_type not in self.entities_mentioned:
            return []
        
        entities = self.entities_mentioned[entity_type]
        sorted_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)
        
        return [entity for entity, count in sorted_entities[:top_n]]
    
    def reset_conversation(self) -> None:
        """Reset conversation state for new conversation"""
        self.conversation_history = []
        self.sentiment_history = []
        self.entities_mentioned = {}
        self.current_topic = None
        self.conversation_start = datetime.now()
        self.turn_count = 0
        # Keep user_info across conversations unless explicitly cleared
    
    def clear_user_info(self) -> None:
        """Clear stored user information"""
        self.user_info = {}
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.conversation_history:
            return {}
        
        duration = datetime.now() - self.conversation_start
        avg_sentiment = sum(s['compound_score'] for s in self.sentiment_history) / len(self.sentiment_history) if self.sentiment_history else 0
        
        return {
            'turn_count': self.turn_count,
            'duration_minutes': duration.total_seconds() / 60,
            'average_sentiment': avg_sentiment,
            'current_topic': self.current_topic,
            'entities_count': sum(len(entities) for entities in self.entities_mentioned.values()),
            'sentiment_trend': self.get_sentiment_trend()
        }
