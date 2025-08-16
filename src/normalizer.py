import re
from typing import Set

# Common stopwords and filler words
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", 
    "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "will", "with",
    "i", "we", "you", "they", "me", "us", "them", "my", "our", "your", "their",
    "this", "that", "these", "those", "here", "there", "when", "where", "how", "why"
}


def normalize_text(text: str) -> str:
    """
    Normalize text for deduplication comparison.
    
    Steps:
    1. Convert to lowercase
    2. Remove URLs and @ mentions
    3. Remove punctuation except spaces
    4. Collapse multiple whitespaces
    5. Remove common stopwords
    6. Strip leading/trailing whitespace
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs (http/https)
    text = re.sub(r'https?://[^\s]+', '', text)
    
    # Remove @ mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    
    # Remove punctuation except spaces and apostrophes
    text = re.sub(r"[^\w\s']", ' ', text)
    
    # Handle contractions (keep them as single words)
    text = re.sub(r"'", '', text)
    
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Split into words and remove stopwords
    words = [word for word in text.split() if word not in STOPWORDS and len(word) > 1]
    
    # Join back and strip
    return ' '.join(words).strip()


def generate_3grams(text: str) -> Set[str]:
    """Generate 3-character grams from normalized text."""
    normalized = normalize_text(text)
    if len(normalized) < 3:
        return {normalized}
    
    grams = set()
    for i in range(len(normalized) - 2):
        gram = normalized[i:i+3]
        if gram.strip():  # Skip grams that are just whitespace
            grams.add(gram)
    
    return grams


def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0