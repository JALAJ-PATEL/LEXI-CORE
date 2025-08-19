# LexiCore

A rule-based Natural Language Processing (NLP) library for conversational AI, built entirely with Python standard libraries without external dependencies.

## Overview

LexiCore is a comprehensive NLP pipeline that provides:

- **Text Preprocessing**: Tokenization, normalization, stemming
- **Linguistic Analysis**: POS tagging, sentiment analysis, entity extraction
- **Dialogue Management**: Intent classification, state tracking, response generation

## Features

### 🔧 Preprocessing
- **Tokenizer**: Regex-based tokenization for words, punctuation, and special characters
- **Normalizer**: Text cleaning, contraction expansion, case normalization
- **Stemmer**: Rule-based stemming to reduce words to root forms

### 🧠 Linguistic Analysis
- **POS Tagger**: Dictionary and suffix-based part-of-speech tagging
- **Sentiment Analyzer**: Lexicon-based sentiment scoring with context awareness
- **Entity Extractor**: Rule-based extraction of names, places, organizations, dates, etc.

### 💬 Dialogue Management
- **Intent Classifier**: Pattern-based intent recognition
- **State Tracker**: Conversation context and user information management
- **Response Generator**: Dynamic response creation using templates and entities

## Project Structure

```
LexiCore/
├── data/                           # JSON data files
│   ├── contractions.json          # Contraction mappings
│   ├── lexicon.json               # Sentiment word lists
│   ├── pos_dictionary.json        # POS dictionary
│   ├── pos_suffix_rules.json      # POS suffix rules
│   └── response_templates.json    # Response templates
│
├── src/                           # Source code
│   ├── preprocessing/             # Text preprocessing
│   ├── linguistic_analysis/       # NLP analysis
│   ├── dialogue_manager/          # Conversation management
│   └── core.py                   # Main pipeline
│
├── tests/                         # Unit tests
├── main.py                       # CLI interface
└── README.md
```

## Quick Start

### Running the CLI

```bash
python main.py
```

This starts an interactive conversation with the LexiCore chatbot.

### Using as a Library

```python
from src.core import LexiCore

# Initialize the NLP pipeline
nlp = LexiCore()

# Process user input
results = nlp.process_input("Hello! My name is Alice.")

# Get the bot's response
print(results['response'])

# Access detailed analysis
print(f"Intent: {results['dialogue_management']['intent']}")
print(f"Sentiment: {results['linguistic_analysis']['sentiment']['sentiment']}")
print(f"Entities: {results['linguistic_analysis']['entities']}")
```

## CLI Commands

- `help` - Show available commands
- `stats` - Display conversation statistics
- `reset` - Reset conversation history
- `debug` - Toggle debug mode to see analysis details
- `quit/exit/bye` - End the conversation

## Components

### Core Pipeline (`src/core.py`)

The main orchestrator that coordinates all NLP components:

```python
# Process text through complete pipeline
results = nlp.process_input("I love this amazing product!")

# Results include:
# - Preprocessing (tokens, normalization, stemming)
# - Linguistic analysis (POS tags, sentiment, entities)
# - Dialogue management (intent, response)
```

### Preprocessing

**Tokenizer** (`src/preprocessing/tokenizer.py`)
- Splits text into tokens using regex patterns
- Handles punctuation, contractions, and special characters

**Normalizer** (`src/preprocessing/normalizer.py`)
- Converts text to lowercase
- Expands contractions ("don't" → "do not")
- Cleans whitespace

**Stemmer** (`src/preprocessing/stemmer.py`)
- Reduces words to root forms using suffix rules
- Handles plurals, verb tenses, adjective forms

### Linguistic Analysis

**POS Tagger** (`src/linguistic_analysis/pos_tagger.py`)
- Tags words with parts of speech
- Uses dictionary lookup and suffix-based rules
- Applies contextual rules for better accuracy

**Sentiment Analyzer** (`src/linguistic_analysis/sentiment_analyzer.py`)
- Analyzes emotional tone using sentiment lexicon
- Handles negation, intensifiers, and diminishers
- Returns polarity scores and overall sentiment

**Entity Extractor** (`src/linguistic_analysis/entity_extractor.py`)
- Extracts named entities (persons, locations, organizations)
- Finds temporal expressions, numbers, emails, URLs
- Rule-based approach with confidence scoring

### Dialogue Management

**Intent Classifier** (`src/dialogue_manager/intent_classifier.py`)
- Classifies user intent using pattern matching
- Supports: greetings, questions, requests, complaints, etc.
- Contextual classification with conversation history

**State Tracker** (`src/dialogue_manager/state_tracker.py`)
- Maintains conversation context and history
- Tracks user information and preferences
- Monitors sentiment trends over time

**Response Generator** (`src/dialogue_manager/response_generator.py`)
- Generates contextual responses using templates
- Incorporates entities and user information
- Adapts tone based on sentiment analysis

## Data Files

### `data/contractions.json`
Mappings for common contractions:
```json
{
  "don't": "do not",
  "can't": "cannot",
  "I'm": "I am"
}
```

### `data/lexicon.json`
Sentiment word lists:
```json
{
  "positive": ["good", "great", "excellent"],
  "negative": ["bad", "terrible", "awful"],
  "neutral": ["maybe", "perhaps", "the"]
}
```

### `data/pos_dictionary.json`
Words categorized by part of speech:
```json
{
  "nouns": ["cat", "dog", "house"],
  "verbs": ["run", "walk", "think"],
  "adjectives": ["good", "fast", "red"]
}
```

### `data/response_templates.json`
Response templates by intent:
```json
{
  "greeting": ["Hello! How can I help you?"],
  "question": ["That's an interesting question about {topic}."],
  "compliment": ["Thank you! That's very kind."]
}
```

## Testing

Run the unit tests:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_tokenizer.py
python tests/test_pos_tagger.py
```

## Configuration

### Processing Options

```python
nlp = LexiCore()

# Configure processing options
nlp.set_processing_options(
    apply_stemming=True,
    extract_entities=True,
    track_sentiment=True,
    generate_response=True
)
```

### Custom Data Directory

```python
# Use custom data directory
nlp = LexiCore(data_dir="/path/to/custom/data")
```

## Example Conversations

```
You: Hello! My name is John.
Bot: Hello John! Nice to meet you! What would you like to talk about?

You: I'm feeling really happy today!
Bot: That's wonderful! Your positive energy is great to hear.

You: Can you help me with something?
Bot: I'd be happy to help you with that. What do you need assistance with?

You: What do you think about artificial intelligence?
Bot: That's an interesting question about artificial intelligence. Here's what I think: it's a fascinating field with many possibilities.
```

## Architecture

LexiCore follows a modular pipeline architecture:

1. **Input** → **Preprocessing** → **Linguistic Analysis** → **Dialogue Management** → **Response**

2. Each component is independent and can be used separately

3. State is maintained across conversation turns

4. All processing uses rule-based approaches with no external ML dependencies

## Limitations

- Rule-based approach may be less accurate than ML models
- Limited to predefined patterns and lexicons
- No learning from conversations (static rules)
- English language focused

## Contributing

This is a standalone educational project demonstrating rule-based NLP techniques. The codebase is designed to be readable and educational.

## License

This project is for educational purposes and demonstrates rule-based NLP techniques using only Python standard libraries.
