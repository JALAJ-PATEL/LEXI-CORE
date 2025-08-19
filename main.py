"""
Main CLI interface for LexiCore conversational AI
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import LexiCore


def main():
    """Main conversation loop"""
    print("=" * 60)
    print("🤖 Welcome to LexiCore - Rule-based Conversational AI")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("Type 'help' for more commands")
    print("-" * 60)
    
    # Initialize the NLP pipeline
    try:
        nlp = LexiCore()
        print("✅ LexiCore initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing LexiCore: {e}")
        return
    
    print("Let's start chatting! 🗣️")
    print()
    
    conversation_active = True
    
    while conversation_active:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                # Process goodbye and then exit
                if user_input.lower() in ['bye', 'goodbye']:
                    results = nlp.process_input(user_input)
                    print(f"Bot: {results['response']}")
                else:
                    print("Bot: Goodbye! Thanks for chatting with me!")
                conversation_active = False
                continue
            
            elif user_input.lower() == 'help':
                show_help()
                continue
            
            elif user_input.lower() == 'stats':
                show_conversation_stats(nlp)
                continue
            
            elif user_input.lower() == 'reset':
                nlp.reset_conversation()
                print("🔄 Conversation reset. Starting fresh!")
                continue
            
            elif user_input.lower() == 'debug':
                toggle_debug_mode(nlp)
                continue
            
            elif not user_input:
                print("Bot: I didn't hear anything. Please say something!")
                continue
            
            # Process user input through LexiCore pipeline
            results = nlp.process_input(user_input)
            
            # Display bot response
            print(f"Bot: {results['response']}")
            
            # Optional: Show debug information
            if hasattr(nlp, 'debug_mode') and nlp.debug_mode:
                show_debug_info(results)
            
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! Thanks for chatting with me!")
            conversation_active = False
        
        except Exception as e:
            print(f"❌ Error processing input: {e}")
            print("Bot: Sorry, I encountered an error. Please try again.")


def show_help():
    """Display help information"""
    print("\n📋 Available Commands:")
    print("  help     - Show this help message")
    print("  stats    - Show conversation statistics")
    print("  reset    - Reset conversation history")
    print("  debug    - Toggle debug mode on/off")
    print("  quit     - Exit the conversation")
    print("  exit     - Exit the conversation")
    print("  bye      - Say goodbye and exit")
    print()


def show_conversation_stats(nlp):
    """Display conversation statistics"""
    state = nlp.get_conversation_state()
    stats = state.get_conversation_stats()
    
    print("\n📊 Conversation Statistics:")
    print(f"  Turns: {stats.get('turn_count', 0)}")
    print(f"  Duration: {stats.get('duration_minutes', 0):.1f} minutes")
    print(f"  Average Sentiment: {stats.get('average_sentiment', 0):.2f}")
    print(f"  Current Topic: {stats.get('current_topic', 'None')}")
    print(f"  Entities Mentioned: {stats.get('entities_count', 0)}")
    print(f"  Sentiment Trend: {stats.get('sentiment_trend', 'neutral')}")
    
    # Show user info if available
    user_name = state.get_user_name()
    if user_name:
        print(f"  Your Name: {user_name}")
    
    preferences = state.get_user_preferences()
    if preferences:
        print(f"  Your Preferences: {', '.join(preferences[:3])}")
    
    print()


def toggle_debug_mode(nlp):
    """Toggle debug mode on/off"""
    if not hasattr(nlp, 'debug_mode'):
        nlp.debug_mode = False
    
    nlp.debug_mode = not nlp.debug_mode
    status = "ON" if nlp.debug_mode else "OFF"
    print(f"🔧 Debug mode: {status}")
    print()


def show_debug_info(results):
    """Display debug information about processing results"""
    print("\n🔍 Debug Information:")
    
    # Preprocessing info
    preprocessing = results.get('preprocessing', {})
    print(f"  Tokens: {preprocessing.get('tokens', [])}")
    print(f"  Token Count: {preprocessing.get('token_count', 0)}")
    
    # Linguistic analysis info
    linguistic = results.get('linguistic_analysis', {})
    sentiment = linguistic.get('sentiment', {})
    print(f"  Sentiment: {sentiment.get('sentiment', 'unknown')} ({sentiment.get('compound_score', 0):.2f})")
    
    pos_stats = linguistic.get('pos_stats', {})
    if pos_stats:
        print(f"  POS Tags: {pos_stats}")
    
    entities = linguistic.get('entities', {})
    entity_count = sum(len(entity_list) for entity_list in entities.values())
    if entity_count > 0:
        print(f"  Entities Found: {entity_count}")
        for entity_type, entity_list in entities.items():
            if entity_list:
                entity_texts = [e.get('text', str(e)) for e in entity_list]
                print(f"    {entity_type}: {entity_texts}")
    
    # Dialogue management info
    dialogue = results.get('dialogue_management', {})
    print(f"  Intent: {dialogue.get('intent', 'unknown')} (confidence: {dialogue.get('intent_confidence', 0):.2f})")
    
    print()


if __name__ == "__main__":
    main()
