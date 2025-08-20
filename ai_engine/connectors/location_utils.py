"""
ai_engine.connectors.location_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Utilities for location-based filtering and prioritization of datasets.
"""

from __future__ import annotations

import re
from typing import List, Optional, Dict, Any


def calculate_location_relevance(
    dataset_metadata: Dict[str, Any], 
    locations: List[str]
) -> float:
    """
    Calculate relevance score for a dataset based on location information.
    
    Args:
        dataset_metadata: Dictionary containing dataset metadata (title, description, etc.)
        locations: List of location strings extracted from the article
        
    Returns:
        Float between 0.0 and 1.0 representing location relevance
    """
    if not locations:
        return 0.0
    
    # Text fields to search for location matches
    searchable_text = []
    
    # Add title and description
    if title := dataset_metadata.get("title", ""):
        searchable_text.append(title.lower())
    if description := dataset_metadata.get("description", ""):
        searchable_text.append(description.lower())
    if notes := dataset_metadata.get("notes", ""):
        searchable_text.append(notes.lower())
    
    # Organization name can also indicate location
    if org := dataset_metadata.get("organization", {}):
        if isinstance(org, dict):
            if org_title := org.get("title", ""):
                searchable_text.append(org_title.lower())
            if org_name := org.get("name", ""):
                searchable_text.append(org_name.lower())
        elif isinstance(org, str):
            searchable_text.append(org.lower())
    
    combined_text = " ".join(searchable_text)
    
    if not combined_text:
        return 0.0
    
    # Score based on location matches
    matches = 0
    total_locations = len(locations)
    
    for location in locations:
        location_lower = location.lower().strip()
        if len(location_lower) < 2:  # Skip very short location names
            continue
            
        # Direct substring match
        if location_lower in combined_text:
            matches += 1
            continue
            
        # Word boundary match (more precise)
        pattern = r'\b' + re.escape(location_lower) + r'\b'
        if re.search(pattern, combined_text):
            matches += 1
            continue
            
        # Partial match for compound locations (e.g., "New York" matching "York")
        location_words = location_lower.split()
        if len(location_words) > 1:
            for word in location_words:
                if len(word) >= 3 and word in combined_text:
                    matches += 0.5  # Partial credit
                    break
    
    # Normalize score
    relevance = matches / total_locations if total_locations > 0 else 0.0
    return min(1.0, relevance)  # Cap at 1.0


def enhance_query_with_locations(
    base_query: str, 
    locations: Optional[List[str]] = None,
    max_locations: int = 2
) -> str:
    """
    Enhance search query by appending location terms.
    
    Args:
        base_query: Original search query
        locations: List of location strings to add
        max_locations: Maximum number of locations to append
        
    Returns:
        Enhanced query string
    """
    if not locations:
        return base_query
    
    # Use only the first few locations to avoid overly long queries
    relevant_locations = locations[:max_locations]
    
    # Filter out very short location names that might cause noise
    filtered_locations = [
        loc.strip() for loc in relevant_locations 
        if len(loc.strip()) >= 2
    ]
    
    if not filtered_locations:
        return base_query
    
    # Append locations to the query
    enhanced_query = base_query
    for location in filtered_locations:
        enhanced_query += f" {location}"
    
    return enhanced_query


def filter_and_sort_by_location_relevance(
    datasets: List[Any], 
    locations: Optional[List[str]] = None,
    location_boost_threshold: float = 0.1
) -> List[Any]:
    """
    Filter and sort datasets by location relevance.
    
    Args:
        datasets: List of dataset objects/dicts
        locations: List of location strings to prioritize
        location_boost_threshold: Minimum relevance score to boost priority
        
    Returns:
        Sorted list of datasets with location-relevant ones first
    """
    if not locations or not datasets:
        return datasets
    
    datasets_with_scores = []
    
    for dataset in datasets:
        # Convert dataset to dict if needed
        if hasattr(dataset, '__dict__'):
            metadata = dataset.__dict__
        elif hasattr(dataset, 'dict'):
            metadata = dataset.dict()
        else:
            metadata = dataset if isinstance(dataset, dict) else {}
        
        relevance_score = calculate_location_relevance(metadata, locations)
        datasets_with_scores.append((dataset, relevance_score))
    
    # Sort by relevance score (descending) then original order
    sorted_datasets = sorted(
        datasets_with_scores, 
        key=lambda x: (-x[1], datasets.index(x[0]))
    )
    
    return [dataset for dataset, _ in sorted_datasets]