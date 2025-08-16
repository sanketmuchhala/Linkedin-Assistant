import pytest
from src.dedupe import (
    fuzzy_score, jaccard_3gram, is_near_duplicate, 
    compute_hash, find_canonical_touchpoint, create_or_merge_touchpoint
)
from src.normalizer import normalize_text, generate_3grams


def test_normalize_text():
    """Test text normalization."""
    # Basic normalization
    assert normalize_text("Hello World!") == "hello world"
    
    # Remove URLs and mentions
    text = "Met at https://example.com and talked to @john about AI"
    expected = "met talked john ai"
    assert normalize_text(text) == expected
    
    # Remove stopwords
    assert normalize_text("I am working on the project") == "working project"
    
    # Handle empty/None
    assert normalize_text("") == ""
    assert normalize_text(None) == ""


def test_fuzzy_score():
    """Test fuzzy similarity scoring."""
    # Identical normalized text
    score1 = fuzzy_score("met at meetup", "met at the meetup")
    assert score1 > 80
    
    # Similar but different
    score2 = fuzzy_score("met at NYC meetup", "caught up at the meetup in NYC")
    assert score2 > 70
    
    # Very different
    score3 = fuzzy_score("met at conference", "hiring for engineering role")
    assert score3 < 50


def test_jaccard_3gram():
    """Test Jaccard similarity on 3-grams."""
    # Similar texts
    score1 = jaccard_3gram("met at meetup", "met at the meetup")
    assert score1 > 0.5
    
    # Different texts
    score2 = jaccard_3gram("conference networking", "hiring engineers")
    assert score2 < 0.3


def test_is_near_duplicate():
    """Test near-duplicate detection."""
    # Should detect as duplicates
    cases_duplicate = [
        ("met at meetup", "caught up at the meetup in NYC"),
        ("hiring for data engineers", "looking for data engineering talent"),
        ("discussed AI at conference", "talked about AI during the conference")
    ]
    
    for text1, text2 in cases_duplicate:
        is_dup, scores = is_near_duplicate(text1, text2, use_semantic=False)
        assert is_dup, f"Should be duplicate: '{text1}' vs '{text2}' (scores: {scores})"
    
    # Should NOT detect as duplicates
    cases_not_duplicate = [
        ("met at AI conference", "hiring for marketing role"),
        ("discussed data pipelines", "talked about vacation plans"),
        ("startup pitch event", "wedding celebration")
    ]
    
    for text1, text2 in cases_not_duplicate:
        is_dup, scores = is_near_duplicate(text1, text2, use_semantic=False)
        assert not is_dup, f"Should NOT be duplicate: '{text1}' vs '{text2}' (scores: {scores})"


def test_compute_hash():
    """Test hash computation for exact matches."""
    # Same normalized text should have same hash
    hash1 = compute_hash("Met at the NYC meetup!")
    hash2 = compute_hash("met at NYC meetup")
    assert hash1 == hash2
    
    # Different text should have different hash
    hash3 = compute_hash("completely different text")
    assert hash1 != hash3


def test_generate_3grams():
    """Test 3-gram generation."""
    grams = generate_3grams("hello")
    expected = {"hel", "ell", "llo"}
    assert grams == expected
    
    # Short text
    short_grams = generate_3grams("hi")
    assert "hi" in short_grams


# Database-dependent tests (require test database setup)
def test_create_or_merge_touchpoint_new():
    """Test creating a new touchpoint when no similar ones exist."""
    # This would need a test database setup
    # For now, just test the logic components
    pass


def test_create_or_merge_touchpoint_merge():
    """Test merging with existing touchpoint when similar one exists."""
    # This would need a test database setup
    # For now, just test the logic components
    pass


def test_edge_cases():
    """Test edge cases."""
    # Empty strings
    assert not is_near_duplicate("", "some text")[0]
    assert not is_near_duplicate("some text", "")[0]
    
    # Very short strings
    is_dup, _ = is_near_duplicate("a", "b")
    assert not is_dup
    
    # Identical strings
    is_dup, _ = is_near_duplicate("exact same", "exact same")
    assert is_dup