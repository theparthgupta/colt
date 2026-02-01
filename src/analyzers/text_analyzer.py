"""
Text Analyzer - Semantic analysis of page text content
"""
import re
from typing import Dict, Any, List, Set
from collections import Counter


class TextAnalyzer:
    def __init__(self, config):
        self.config = config
        
    def analyze_text(self, text: str, html_content: str = '') -> Dict[str, Any]:
        """Perform comprehensive text analysis"""
        analysis = {}
        
        if self.config.ANALYZE_TEXT_SEMANTICS:
            analysis['keywords'] = self._extract_keywords(text)
            analysis['entities'] = self._extract_entities(text)
            analysis['patterns'] = self._extract_patterns(text)
            analysis['sentiment_indicators'] = self._analyze_sentiment_indicators(text)
        
        if self.config.ANALYZE_TEXT_STRUCTURE:
            analysis['structure'] = self._analyze_structure(html_content)
            analysis['readability'] = self._analyze_readability(text)
        
        if self.config.EXTRACT_DATA_PATTERNS:
            analysis['data_patterns'] = self._extract_data_patterns(text)
        
        return analysis
    
    def _extract_keywords(self, text: str) -> Dict[str, Any]:
        """Extract keywords using frequency analysis"""
        # Clean text
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        top_keywords = word_freq.most_common(20)
        
        # Calculate bi-grams (2-word phrases)
        bigrams = []
        for i in range(len(filtered_words) - 1):
            bigrams.append(f"{filtered_words[i]} {filtered_words[i+1]}")
        
        bigram_freq = Counter(bigrams)
        top_bigrams = bigram_freq.most_common(10)
        
        return {
            'top_keywords': [{'word': w, 'count': c} for w, c in top_keywords],
            'top_phrases': [{'phrase': p, 'count': c} for p, c in top_bigrams],
            'unique_words': len(set(filtered_words)),
            'total_words': len(filtered_words),
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (simple pattern-based)"""
        entities = {
            'emails': [],
            'phone_numbers': [],
            'urls': [],
            'dates': [],
            'times': [],
            'money': [],
            'percentages': [],
            'capitalized_phrases': [],
        }
        
        # Emails
        entities['emails'] = list(set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)))
        
        # Phone numbers
        entities['phone_numbers'] = list(set(re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)))
        entities['phone_numbers'].extend(re.findall(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', text))
        
        # URLs
        entities['urls'] = list(set(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)))
        
        # Dates (various formats)
        entities['dates'] = list(set(re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)))
        entities['dates'].extend(re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b', text))
        
        # Times
        entities['times'] = list(set(re.findall(r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b', text)))
        
        # Money
        entities['money'] = list(set(re.findall(r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?', text)))
        
        # Percentages
        entities['percentages'] = list(set(re.findall(r'\b\d+(?:\.\d+)?%', text)))
        
        # Capitalized phrases (potential names, titles)
        entities['capitalized_phrases'] = list(set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)))[:20]
        
        return entities
    
    def _extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract common patterns"""
        patterns = {
            'hashtags': list(set(re.findall(r'#\w+', text))),
            'mentions': list(set(re.findall(r'@\w+', text))),
            'codes': list(set(re.findall(r'\b[A-Z0-9]{6,}\b', text)))[:10],  # Codes/IDs
            'zip_codes': list(set(re.findall(r'\b\d{5}(?:-\d{4})?\b', text))),
            'credit_cards': list(set(re.findall(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', text))),
            'ssn': list(set(re.findall(r'\b\d{3}-\d{2}-\d{4}\b', text))),
        }
        
        return patterns
    
    def _analyze_sentiment_indicators(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment indicators"""
        text_lower = text.lower()
        
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'best', 'perfect', 'awesome', 'happy', 'pleased', 'satisfied',
            'beautiful', 'brilliant', 'success', 'successful', 'win', 'winner',
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'disappointed', 'disappointing', 'fail', 'failed', 'failure', 'wrong',
            'error', 'problem', 'issue', 'broken', 'bug', 'sad', 'angry',
        }
        
        urgent_words = {
            'urgent', 'immediately', 'asap', 'critical', 'emergency', 'important',
            'attention', 'required', 'must', 'deadline', 'expires', 'limited',
        }
        
        action_words = {
            'buy', 'purchase', 'order', 'subscribe', 'register', 'sign up',
            'download', 'install', 'try', 'start', 'join', 'click', 'get',
            'learn', 'discover', 'explore', 'save', 'earn', 'win',
        }
        
        words = set(re.findall(r'\b[a-z]+\b', text_lower))
        
        return {
            'positive_count': len(words & positive_words),
            'negative_count': len(words & negative_words),
            'urgent_count': len(words & urgent_words),
            'action_count': len(words & action_words),
            'positive_words': list(words & positive_words),
            'negative_words': list(words & negative_words),
            'urgent_words': list(words & urgent_words),
            'action_words': list(words & action_words),
        }
    
    def _analyze_structure(self, html_content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        # Count heading levels
        h1_count = len(re.findall(r'<h1[^>]*>', html_content))
        h2_count = len(re.findall(r'<h2[^>]*>', html_content))
        h3_count = len(re.findall(r'<h3[^>]*>', html_content))
        h4_count = len(re.findall(r'<h4[^>]*>', html_content))
        h5_count = len(re.findall(r'<h5[^>]*>', html_content))
        h6_count = len(re.findall(r'<h6[^>]*>', html_content))
        
        # Count structural elements
        p_count = len(re.findall(r'<p[^>]*>', html_content))
        ul_count = len(re.findall(r'<ul[^>]*>', html_content))
        ol_count = len(re.findall(r'<ol[^>]*>', html_content))
        table_count = len(re.findall(r'<table[^>]*>', html_content))
        
        return {
            'heading_distribution': {
                'h1': h1_count,
                'h2': h2_count,
                'h3': h3_count,
                'h4': h4_count,
                'h5': h5_count,
                'h6': h6_count,
            },
            'has_proper_h1': h1_count == 1,  # SEO best practice
            'total_paragraphs': p_count,
            'total_lists': ul_count + ol_count,
            'total_tables': table_count,
        }
    
    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Analyze text readability"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return {}
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (rough approximation)
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / len(words) if words else 0
        
        # Flesch Reading Ease (rough approximation)
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = max(0, min(100, flesch_score))  # Clamp to 0-100
        
        return {
            'total_sentences': len(sentences),
            'total_words': len(words),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2),
            'flesch_reading_ease': round(flesch_score, 2),
            'readability_level': self._get_readability_level(flesch_score),
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (rough approximation)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _get_readability_level(self, flesch_score: float) -> str:
        """Get readability level from Flesch score"""
        if flesch_score >= 90:
            return 'Very Easy (5th grade)'
        elif flesch_score >= 80:
            return 'Easy (6th grade)'
        elif flesch_score >= 70:
            return 'Fairly Easy (7th grade)'
        elif flesch_score >= 60:
            return 'Standard (8th-9th grade)'
        elif flesch_score >= 50:
            return 'Fairly Difficult (10th-12th grade)'
        elif flesch_score >= 30:
            return 'Difficult (College)'
        else:
            return 'Very Difficult (College graduate)'
    
    def _extract_data_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract data patterns for agent use"""
        return {
            'api_endpoints': list(set(re.findall(r'/api/[\w/-]+', text))),
            'routes': list(set(re.findall(r'/[\w/-]+', text)))[:20],
            'file_paths': list(set(re.findall(r'[\w/]+\.\w{2,4}', text)))[:20],
            'variables': list(set(re.findall(r'\b[a-z_][a-z0-9_]*\b', text)))[:30],
            'numbers': list(set(re.findall(r'\b\d+\b', text)))[:20],
        }