"""
Mapping rules between angle topics and dataset tags.

This module defines the logic for matching editorial angles with relevant datasets
based on topic-tag mapping rules.
"""

from typing import List, Dict, Set
import re
from ai_engine.schemas import DatasetSuggestion


# Predefined topic-tag mapping rules
TOPIC_TAG_MAPPING: Dict[str, Set[str]] = {
    # Economics and Finance topics
    "économie": {"economy", "economics", "finance", "budget", "revenue", "expenses", "gdp"},
    "finance": {"finance", "banking", "investment", "budget", "economy", "revenue"},
    "budget": {"budget", "finance", "spending", "revenue", "economics", "government"},
    
    # Social topics
    "social": {"social", "welfare", "benefits", "society", "demographics", "population"},
    "éducation": {"education", "school", "university", "training", "learning", "students"},
    "santé": {"health", "healthcare", "medical", "hospital", "disease", "public health"},
    "emploi": {"employment", "jobs", "labor", "unemployment", "workforce", "career"},
    
    # Environment topics
    "environnement": {"environment", "climate", "pollution", "air quality", "emissions", "energy"},
    "climat": {"climate", "weather", "temperature", "environment", "emissions", "carbon"},
    "énergie": {"energy", "renewable", "electricity", "consumption", "power", "environment"},
    
    # Urban and Infrastructure topics
    "transport": {"transport", "traffic", "mobility", "public transport", "infrastructure"},
    "logement": {"housing", "real estate", "property", "accommodation", "urban planning"},
    "urbanisme": {"urban planning", "city", "development", "infrastructure", "zoning"},
    
    # Political topics
    "politique": {"politics", "government", "policy", "administration", "governance"},
    "gouvernement": {"government", "administration", "public", "policy", "politics"},
    
    # Cultural topics
    "culture": {"culture", "arts", "heritage", "museum", "cultural activities", "events"},
    "tourisme": {"tourism", "travel", "attractions", "hospitality", "cultural sites"},
}


def normalize_topic(topic: str) -> str:
    """Normalize a topic string for matching."""
    if not topic:
        return ""
    
    # Convert to lowercase and remove accents/special chars for better matching
    normalized = topic.lower().strip()
    
    # Remove common prefixes/suffixes
    normalized = re.sub(r'\b(le|la|les|de|du|des|un|une)\b', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized


def normalize_tag(tag: str) -> str:
    """Normalize a tag string for matching."""
    if not tag:
        return ""
    
    return tag.lower().strip().replace('-', ' ').replace('_', ' ')


def calculate_topic_tag_score(topic: str, tags: List[str]) -> float:
    """
    Calculate a relevance score between an angle topic and dataset tags.
    
    Args:
        topic: The angle topic
        tags: List of dataset tags
        
    Returns:
        Score between 0.0 and 1.0 indicating relevance
    """
    if not topic or not tags:
        return 0.0
    
    normalized_topic = normalize_topic(topic)
    normalized_tags = [normalize_tag(tag) for tag in tags]
    
    # Direct mapping lookup
    if normalized_topic in TOPIC_TAG_MAPPING:
        expected_tags = TOPIC_TAG_MAPPING[normalized_topic]
        matching_tags = sum(1 for tag in normalized_tags 
                          if any(expected in tag or tag in expected 
                                for expected in expected_tags))
        if matching_tags > 0:
            return min(1.0, matching_tags / len(expected_tags) + 0.3)
    
    # Fuzzy matching - check if topic words appear in tags
    topic_words = set(normalized_topic.split())
    tag_words = set()
    for tag in normalized_tags:
        tag_words.update(tag.split())
    
    word_matches = len(topic_words & tag_words)
    if word_matches > 0:
        return min(1.0, word_matches / len(topic_words))
    
    return 0.0


def filter_datasets_by_topic(topic: str, datasets: List[DatasetSuggestion], 
                           min_score: float = 0.2) -> List[DatasetSuggestion]:
    """
    Filter datasets based on topic-tag mapping relevance.
    
    Args:
        topic: The angle topic to match against
        datasets: List of datasets to filter
        min_score: Minimum relevance score (0.0-1.0)
        
    Returns:
        Filtered list of datasets with relevance scores
    """
    if not topic:
        return datasets
    
    filtered = []
    for dataset in datasets:
        score = calculate_topic_tag_score(topic, dataset.tags)
        if score >= min_score:
            # Add score as metadata (without modifying the original object)
            dataset_copy = dataset.model_copy()
            if hasattr(dataset_copy, '__dict__'):
                dataset_copy.__dict__['relevance_score'] = score
            filtered.append(dataset_copy)
    
    # Sort by relevance score (highest first)
    filtered.sort(key=lambda d: getattr(d, 'relevance_score', 0.0), reverse=True)
    return filtered


def suggest_topic_for_angle(title: str, description: str) -> str:
    """
    Suggest a topic for an angle based on its title and description.
    
    Args:
        title: Angle title
        description: Angle description
        
    Returns:
        Suggested topic string
    """
    text = f"{title} {description}".lower()
    
    # Look for direct topic matches in the text
    for topic, keywords in TOPIC_TAG_MAPPING.items():
        # Check if topic name appears in text
        if topic in text:
            return topic
        
        # Check if any of the topic's associated keywords appear
        for keyword in keywords:
            if keyword in text:
                return topic
    
    # Fallback: extract main noun/subject from title
    words = title.lower().split()
    common_words = {'de', 'du', 'des', 'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'pour', 'dans', 'sur'}
    content_words = [w for w in words if w not in common_words and len(w) > 2]
    
    if content_words:
        return content_words[0]  # Return first meaningful word
    
    return ""


def generate_tags_for_dataset(title: str, description: str, source_name: str) -> List[str]:
    """
    Generate relevant tags for a dataset based on its metadata.
    
    Args:
        title: Dataset title
        description: Dataset description
        source_name: Source name (e.g., "data.gouv.fr")
        
    Returns:
        List of generated tags
    """
    tags = set()
    text = f"{title} {description}".lower() if description else title.lower()
    
    # Extract tags from text based on known topics
    for topic, keywords in TOPIC_TAG_MAPPING.items():
        for keyword in keywords:
            if keyword in text:
                tags.add(keyword)
                # Add related terms
                if topic in TOPIC_TAG_MAPPING:
                    tags.update(list(TOPIC_TAG_MAPPING[topic])[:2])  # Add 2 related terms
    
    # Add source-specific tags
    if "gouv" in source_name:
        tags.add("government")
        tags.add("public")
    elif "eurostat" in source_name:
        tags.add("statistics")
        tags.add("europe")
    elif "data.gov" in source_name:
        tags.add("government")
        tags.add("usa")
    
    return sorted(list(tags))