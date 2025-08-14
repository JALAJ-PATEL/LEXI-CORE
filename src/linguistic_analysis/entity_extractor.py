"""
Rule-based entity extraction for names, objects, etc.
"""
import re
from typing import List, Dict, Tuple


class EntityExtractor:
    """
    Rule-based named entity extractor
    """
    
    def __init__(self):
        # Common person name patterns
        self.person_titles = ['mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam']
        self.person_suffixes = ['jr', 'sr', 'ii', 'iii', 'iv']
        
        # Common location indicators
        self.location_indicators = ['city', 'town', 'village', 'country', 'state', 'province', 
                                  'street', 'avenue', 'road', 'lane', 'boulevard']
        
        # Organization indicators
        self.org_indicators = ['company', 'corp', 'corporation', 'inc', 'ltd', 'llc', 
                             'university', 'college', 'school', 'hospital', 'bank']
        
        # Time expressions
        self.time_patterns = {
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'time': r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?\b',
            'year': r'\b(?:19|20)\d{2}\b',
            'month': r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b'
        }
        
        # Number patterns
        self.number_patterns = {
            'integer': r'\b\d+\b',
            'decimal': r'\b\d+\.\d+\b',
            'percentage': r'\b\d+(?:\.\d+)?%\b',
            'currency': r'\$\d+(?:\.\d{2})?\b'
        }
    
    def extract_entities(self, tokens: List[str], pos_tags: List[Tuple[str, str]] = None) -> Dict[str, List[Dict]]:
        """
        Extract entities from a list of tokens
        
        Args:
            tokens (List[str]): List of tokens
            pos_tags (List[Tuple[str, str]]): Optional POS tags
            
        Returns:
            Dict[str, List[Dict]]: Extracted entities by category
        """
        text = ' '.join(tokens)
        entities = {
            'PERSON': [],
            'LOCATION': [],
            'ORGANIZATION': [],
            'TIME': [],
            'NUMBER': [],
            'EMAIL': [],
            'URL': [],
            'PHONE': []
        }
        
        # Extract different types of entities
        entities['PERSON'].extend(self._extract_persons(tokens, pos_tags))
        entities['LOCATION'].extend(self._extract_locations(tokens))
        entities['ORGANIZATION'].extend(self._extract_organizations(tokens))
        entities['TIME'].extend(self._extract_time_expressions(text))
        entities['NUMBER'].extend(self._extract_numbers(text))
        entities['EMAIL'].extend(self._extract_emails(text))
        entities['URL'].extend(self._extract_urls(text))
        entities['PHONE'].extend(self._extract_phone_numbers(text))
        
        return entities
    
    def _extract_persons(self, tokens: List[str], pos_tags: List[Tuple[str, str]] = None) -> List[Dict]:
        """Extract person names"""
        persons = []
        
        # Look for capitalized word sequences (potential names)
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for titles
            if token.lower() in self.person_titles:
                name_parts = [token]
                j = i + 1
                
                # Collect following capitalized words
                while j < len(tokens) and tokens[j][0].isupper() and tokens[j].isalpha():
                    name_parts.append(tokens[j])
                    j += 1
                
                if len(name_parts) > 1:  # Title + at least one name
                    persons.append({
                        'text': ' '.join(name_parts),
                        'start': i,
                        'end': j - 1,
                        'confidence': 0.8
                    })
                    i = j
                    continue
            
            # Look for capitalized sequences without titles
            if token[0].isupper() and token.isalpha() and len(token) > 1:
                name_parts = [token]
                j = i + 1
                
                # Collect following capitalized words
                while (j < len(tokens) and 
                       tokens[j][0].isupper() and 
                       tokens[j].isalpha() and 
                       len(tokens[j]) > 1):
                    name_parts.append(tokens[j])
                    j += 1
                
                # Check for suffixes
                if (j < len(tokens) and 
                    tokens[j].lower().rstrip('.,') in self.person_suffixes):
                    name_parts.append(tokens[j])
                    j += 1
                
                # Consider it a person name if 2+ parts or single name after "I'm" etc.
                if len(name_parts) >= 2:
                    persons.append({
                        'text': ' '.join(name_parts),
                        'start': i,
                        'end': j - 1,
                        'confidence': 0.6
                    })
                    i = j
                    continue
            
            i += 1
        
        return persons
    
    def _extract_locations(self, tokens: List[str]) -> List[Dict]:
        """Extract location names"""
        locations = []
        
        for i, token in enumerate(tokens):
            token_lower = token.lower()
            
            # Check for location indicators
            if token_lower in self.location_indicators:
                # Look for preceding capitalized words
                start_idx = i
                while start_idx > 0 and tokens[start_idx - 1][0].isupper():
                    start_idx -= 1
                
                if start_idx < i:
                    location_text = ' '.join(tokens[start_idx:i + 1])
                    locations.append({
                        'text': location_text,
                        'start': start_idx,
                        'end': i,
                        'confidence': 0.7
                    })
        
        return locations
    
    def _extract_organizations(self, tokens: List[str]) -> List[Dict]:
        """Extract organization names"""
        organizations = []
        
        for i, token in enumerate(tokens):
            token_lower = token.lower().rstrip('.,')
            
            # Check for organization indicators
            if token_lower in self.org_indicators:
                # Look for preceding capitalized words
                start_idx = i
                while start_idx > 0 and tokens[start_idx - 1][0].isupper():
                    start_idx -= 1
                
                if start_idx < i:
                    org_text = ' '.join(tokens[start_idx:i + 1])
                    organizations.append({
                        'text': org_text,
                        'start': start_idx,
                        'end': i,
                        'confidence': 0.7
                    })
        
        return organizations
    
    def _extract_time_expressions(self, text: str) -> List[Dict]:
        """Extract time expressions using regex patterns"""
        time_entities = []
        
        for time_type, pattern in self.time_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                time_entities.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': time_type,
                    'confidence': 0.9
                })
        
        return time_entities
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """Extract numeric expressions"""
        number_entities = []
        
        for number_type, pattern in self.number_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                number_entities.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': number_type,
                    'confidence': 0.95
                })
        
        return number_entities
    
    def _extract_emails(self, text: str) -> List[Dict]:
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = []
        
        matches = re.finditer(email_pattern, text)
        for match in matches:
            emails.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.95
            })
        
        return emails
    
    def _extract_urls(self, text: str) -> List[Dict]:
        """Extract URLs"""
        url_pattern = r'https?://[^\s]+'
        urls = []
        
        matches = re.finditer(url_pattern, text)
        for match in matches:
            urls.append({
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.95
            })
        
        return urls
    
    def _extract_phone_numbers(self, text: str) -> List[Dict]:
        """Extract phone numbers"""
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                phones.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9
                })
        
        return phones
