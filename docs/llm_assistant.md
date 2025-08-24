# LLM Assistant for Verified Sources

This document describes the new LLM Assistant role that provides verified source suggestions for journalistic investigations.

## Overview

The LLM Assistant extends the DataScope AI platform by suggesting credible and verified sources beyond just open datasets. These sources include reports, academic studies, official documentation, and articles from reputable organizations.

## Features

### 1. Verified Source Suggestions
- Suggests credible sources for each editorial angle
- Includes reports, studies, articles, and official documentation
- Provides credibility scoring (1-10)
- Filters for accessible sources (no paywall/restricted access)

### 2. Model Selection and Configuration
- Configurable LLM model selection
- Support for multiple OpenAI models (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
- Adjustable temperature and token limits
- Cost and speed optimization options

### 3. Integration with Existing Pipeline
- Seamlessly integrated into the main analysis pipeline
- Sources are provided alongside existing dataset suggestions
- Maintains compatibility with existing functionality

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```bash
# LLM Assistant Configuration
ASSISTANT_MODEL=gpt-4o-mini          # Default model for the assistant
ASSISTANT_TEMPERATURE=0.3            # Temperature for response generation (0.0-1.0)
ASSISTANT_MAX_TOKENS=2000           # Maximum tokens per response
```

### Available Models

The assistant supports the following models:

- `gpt-4o-mini`: Low cost, fast responses (default)
- `gpt-4o`: High quality, higher cost
- `gpt-3.5-turbo`: Legacy model, low cost

## Usage

### Basic Usage

The assistant is automatically integrated into the main pipeline. When you run an analysis, verified sources will be included in the results:

```python
from ai_engine.pipeline import run

# Run analysis on an article
package, markdown, score, angle_resources = run("Your article text here")

# Access verified sources for each angle
for resource in angle_resources:
    print(f"Angle: {resource.title}")
    for source in resource.verified_sources:
        print(f"  - {source.title} (Score: {source.credibility_score}/10)")
        print(f"    {source.description}")
        print(f"    {source.link}")
```

### Direct Assistant Usage

You can also use the assistant directly:

```python
from ai_engine.assistant.verified_sources import run, get_assistant_info
from ai_engine.schemas import AngleResult, Angle

# Create angle result
angle_result = AngleResult(
    language="fr",
    angles=[
        Angle(
            title="Impact du changement climatique",
            rationale="Analyser les effets du réchauffement climatique"
        )
    ]
)

# Get verified sources
sources_per_angle = run(angle_result)

# Check assistant configuration
info = get_assistant_info()
print(f"Current model: {info['model']}")
print(f"Available models: {list(info['available_models'].keys())}")
```

### Model Override

You can specify a different model for specific requests:

```python
# Use a higher-quality model for important analysis
sources = run(angle_result, model_name="gpt-4o")
```

## Source Types

The assistant categorizes sources into the following types:

- `report`: Official reports and studies
- `article`: News articles and journalistic pieces
- `study`: Academic research and scientific studies
- `documentation`: Technical and official documentation
- `official`: Government and institutional publications

## Schema

### VerifiedSource

```python
class VerifiedSource(BaseModel):
    title: str                    # Title of the source
    description: str              # Description of relevance and credibility
    link: str                     # URL to the source
    source: str                   # Organization/publication name
    source_type: str              # Type: 'report', 'article', 'study', etc.
    credibility_score: int        # Score from 1-10 (default: 5)
    publication_date: str | None  # Publication date if available
    language: str                 # Language (default: "fr")
    angle_idx: int               # Associated editorial angle index
```

## Quality Guidelines

The assistant is designed to suggest sources that are:

1. **Credible and authoritative**: From official organizations, research institutions, or established publications
2. **Accessible**: No paywall or special access requirements
3. **Relevant**: Directly related to the editorial angle
4. **Recent**: Current or historically relevant information
5. **Reputable**: From trusted sources and institutions

## Integration Points

### Pipeline Integration

The assistant is integrated at step 6.1 in the main pipeline:

1. Extract entities
2. Generate editorial angles
3. Generate keywords
4. Find datasets via connectors
5. Find data sources via LLM
6. **Find verified sources via LLM Assistant** ← New step
7. Generate visualization suggestions
8. Combine all resources

### AngleResources Schema

The `AngleResources` schema now includes a `verified_sources` field:

```python
class AngleResources(BaseModel):
    index: int
    title: str
    description: str
    keywords: List[str]
    datasets: List[DatasetSuggestion]      # From connectors
    sources: List[LLMSourceSuggestion]     # Data sources from LLM
    verified_sources: List[VerifiedSource] # New: Verified sources from assistant
    visualizations: List[VizSuggestion]
```

## Error Handling

The assistant includes robust error handling:

- Network failures return empty source lists
- Invalid responses are gracefully handled
- Errors are logged but don't break the pipeline
- Fallback to empty results ensures pipeline continues

## Testing

Run the assistant tests:

```bash
USE_SQLITE_FOR_TESTS=1 python -m pytest ai_engine/tests/test_verified_sources.py -v
USE_SQLITE_FOR_TESTS=1 python -m pytest ai_engine/tests/test_assistant_integration.py -v
```

## Future Enhancements

Potential future improvements:

1. **Multi-language Support**: Enhanced prompts for different languages
2. **Source Validation**: Automatic checking of source accessibility
3. **Specialized Models**: Domain-specific models for different topics
4. **User Feedback**: Learning from user ratings of source quality
5. **Caching**: Intelligent caching of frequent source requests