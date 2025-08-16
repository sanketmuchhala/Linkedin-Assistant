import hashlib
from typing import List, Optional, Tuple
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from .models import Touchpoint
from .normalizer import normalize_text, generate_3grams, jaccard_similarity

# Similarity thresholds
FUZZY_THRESHOLD = 86
JACCARD_THRESHOLD = 0.86
SEMANTIC_THRESHOLD = 0.86

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDINGS_AVAILABLE = True
    
    # Initialize model lazily
    _model = None
    
    def get_model():
        global _model
        if _model is None:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        return _model
        
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    
    def get_model():
        return None


def compute_hash(text: str) -> str:
    """Compute a hash for exact duplicate detection."""
    normalized = normalize_text(text)
    return hashlib.md5(normalized.encode()).hexdigest()


def fuzzy_score(text1: str, text2: str) -> float:
    """Compute fuzzy similarity using token_set_ratio."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return fuzz.token_set_ratio(norm1, norm2)


def jaccard_3gram(text1: str, text2: str) -> float:
    """Compute Jaccard similarity on 3-grams."""
    grams1 = generate_3grams(text1)
    grams2 = generate_3grams(text2)
    return jaccard_similarity(grams1, grams2)


def semantic_similarity(text1: str, text2: str) -> float:
    """Compute semantic similarity using embeddings (if available)."""
    if not EMBEDDINGS_AVAILABLE:
        return 0.0
    
    try:
        model = get_model()
        if model is None:
            return 0.0
            
        embeddings = model.encode([text1, text2])
        
        # Compute cosine similarity
        dot_product = np.dot(embeddings[0], embeddings[1])
        norm1 = np.linalg.norm(embeddings[0])
        norm2 = np.linalg.norm(embeddings[1])
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    except Exception:
        return 0.0


def is_near_duplicate(text1: str, text2: str, use_semantic: bool = True) -> Tuple[bool, dict]:
    """
    Determine if two texts are near-duplicates.
    
    Returns:
        (is_duplicate, scores_dict)
    """
    if not text1.strip() or not text2.strip():
        return False, {}
    
    # Compute similarity scores
    fuzzy = fuzzy_score(text1, text2)
    jaccard = jaccard_3gram(text1, text2) * 100  # Convert to 0-100 scale
    semantic = semantic_similarity(text1, text2) * 100 if use_semantic else 0
    
    scores = {
        "fuzzy": fuzzy,
        "jaccard": jaccard,
        "semantic": semantic
    }
    
    # Check thresholds
    fuzzy_match = fuzzy >= FUZZY_THRESHOLD
    jaccard_match = jaccard >= (JACCARD_THRESHOLD * 100)
    semantic_match = semantic >= (SEMANTIC_THRESHOLD * 100) if use_semantic else False
    
    # Consider it a duplicate if fuzzy OR jaccard OR semantic similarity is high
    is_duplicate = fuzzy_match or jaccard_match or semantic_match
    
    return is_duplicate, scores


def find_canonical_touchpoint(db: Session, contact_id: int, new_context: str) -> Optional[Touchpoint]:
    """
    Find if there's a canonical touchpoint that matches the new context.
    
    Returns the canonical touchpoint if found, None otherwise.
    """
    # Get all canonical touchpoints for this contact
    canonical_touchpoints = db.query(Touchpoint).filter(
        Touchpoint.contact_id == contact_id,
        Touchpoint.is_canonical == 1
    ).all()
    
    # Check for exact hash match first
    new_hash = compute_hash(new_context)
    for tp in canonical_touchpoints:
        if tp.dedupe_hash == new_hash:
            return tp
    
    # Check for near-duplicates
    for tp in canonical_touchpoints:
        is_dup, scores = is_near_duplicate(new_context, tp.context)
        if is_dup:
            return tp
    
    return None


def create_or_merge_touchpoint(db: Session, contact_id: int, context: str) -> Tuple[Touchpoint, bool]:
    """
    Create a new touchpoint or merge with existing canonical one.
    
    Returns:
        (touchpoint, was_merged)
    """
    canonical = find_canonical_touchpoint(db, contact_id, context)
    
    if canonical:
        # Create a non-canonical touchpoint linked to the canonical one
        touchpoint = Touchpoint(
            contact_id=contact_id,
            context=context,
            dedupe_hash=compute_hash(context),
            similarity_group=canonical.similarity_group or str(canonical.id),
            is_canonical=0
        )
        db.add(touchpoint)
        db.flush()
        return touchpoint, True
    else:
        # Create a new canonical touchpoint
        touchpoint = Touchpoint(
            contact_id=contact_id,
            context=context,
            dedupe_hash=compute_hash(context),
            similarity_group=None,
            is_canonical=1
        )
        db.add(touchpoint)
        db.flush()
        
        # Set similarity group to the touchpoint ID
        touchpoint.similarity_group = str(touchpoint.id)
        db.add(touchpoint)
        db.flush()
        
        return touchpoint, False


def merge_duplicate_touchpoints(db: Session, contact_id: int) -> dict:
    """
    Find and merge duplicate touchpoints for a contact.
    
    Returns a summary of the merge operation.
    """
    touchpoints = db.query(Touchpoint).filter(
        Touchpoint.contact_id == contact_id
    ).order_by(Touchpoint.created_at).all()
    
    if len(touchpoints) <= 1:
        return {"total": len(touchpoints), "merged": 0, "groups": 0}
    
    groups = {}
    merged_count = 0
    
    for i, tp1 in enumerate(touchpoints):
        if tp1.is_canonical == 0:  # Skip already processed non-canonical touchpoints
            continue
            
        group_key = tp1.similarity_group or str(tp1.id)
        if group_key not in groups:
            groups[group_key] = {"canonical": tp1, "duplicates": []}
        
        # Find duplicates
        for j, tp2 in enumerate(touchpoints[i+1:], i+1):
            if tp2.is_canonical == 0:  # Skip already processed
                continue
                
            is_dup, _ = is_near_duplicate(tp1.context, tp2.context)
            if is_dup:
                # Mark tp2 as non-canonical
                tp2.is_canonical = 0
                tp2.similarity_group = group_key
                groups[group_key]["duplicates"].append(tp2)
                merged_count += 1
    
    # Commit changes
    db.commit()
    
    return {
        "total": len(touchpoints),
        "merged": merged_count,
        "groups": len(groups)
    }