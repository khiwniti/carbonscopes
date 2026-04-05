# SPARQL Query Library Guide

## Overview

The SPARQL Query Library provides high-level Python functions for querying TGO (Thailand Greenhouse Gas Management Organization) construction material emission factors from GraphDB.

**Module:** `core.knowledge_graph.sparql_queries`

**Key Features:**
- Material emission factor lookups by URI
- Full-text material search with bilingual support (Thai/English)
- Category-based material filtering
- Data quality checks (staleness detection)
- RDFS inference for automatic subclass queries
- Decimal precision for emission factors (consultant-grade accuracy)

**Performance Targets:**
- Direct lookups: <50ms
- Category queries: <200ms
- Full-text search: <500ms

---

## Installation & Setup

```python
from core.knowledge_graph import (
    GraphDBClient,
    get_emission_factor,
    search_materials,
    list_materials_by_category,
    get_all_categories,
    find_stale_materials,
)

# Initialize GraphDB client
client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")

# Test connection
client.test_connection()
```

---

## Functions

### 1. get_emission_factor()

Retrieve the emission factor for a specific material by URI.

**Signature:**
```python
get_emission_factor(
    client: GraphDBClient,
    material_id: str,
    version: Optional[str] = None,
    include_metadata: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `client`: GraphDBClient instance
- `material_id`: Material URI (e.g., `"http://tgo.or.th/materials/concrete-c30"`)
- `version`: Optional version URI for querying specific data versions
- `include_metadata`: If True, includes source document, data quality, uncertainty

**Returns:**
```python
{
    'material_id': 'http://tgo.or.th/materials/concrete-c30',
    'emission_factor': Decimal('445.6'),
    'unit': 'kgCO2e/m³',
    'label_en': 'Ready-mixed Concrete C30',
    'label_th': 'คอนกรีตผสมเสร็จ C30',
    'category': 'Concrete',
    'effective_date': '2026-01-01',
    'metadata': {  # Only if include_metadata=True
        'source_document': 'https://thaicarbonlabel.tgo.or.th/...',
        'data_quality': 'Verified',
        'uncertainty': Decimal('0.10'),
        'geographic_scope': 'Thailand'
    }
}
```

**Example:**
```python
# Basic usage
result = get_emission_factor(client, "http://tgo.or.th/materials/concrete-c30")
print(f"Emission factor: {result['emission_factor']} {result['unit']}")
# Output: Emission factor: 445.6 kgCO2e/m³

# With full metadata
result = get_emission_factor(
    client,
    "http://tgo.or.th/materials/concrete-c30",
    include_metadata=True
)
print(f"Data quality: {result['metadata']['data_quality']}")
print(f"Uncertainty: ±{result['metadata']['uncertainty'] * 100}%")

# Query specific version
result = get_emission_factor(
    client,
    "http://tgo.or.th/materials/concrete-c30",
    version="http://tgo.or.th/versions/2026-03"
)
```

**Exceptions:**
- `MaterialNotFoundError`: If material URI is not found
- `QueryError`: If SPARQL query fails

---

### 2. search_materials()

Search for materials by name using full-text matching.

**Signature:**
```python
search_materials(
    client: GraphDBClient,
    query_string: str,
    language: str = "en",
    limit: int = 20,
    category_filter: Optional[str] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `client`: GraphDBClient instance
- `query_string`: Search string (case-insensitive, regex supported)
- `language`: Language for label matching ("en" or "th")
- `limit`: Maximum number of results (default: 20)
- `category_filter`: Optional category filter (e.g., "Concrete", "Steel")

**Returns:**
```python
[
    {
        'material_id': 'http://tgo.or.th/materials/concrete-c30',
        'label': 'Ready-mixed Concrete C30',
        'category': 'Concrete',
        'emission_factor': Decimal('445.6'),
        'unit': 'kgCO2e/m³',
        'effective_date': '2026-01-01'
    },
    # ... more results
]
```

**Examples:**
```python
# Search for concrete materials
results = search_materials(client, "concrete")
for material in results:
    print(f"{material['label']}: {material['emission_factor']} {material['unit']}")

# Search in Thai
results = search_materials(client, "คอนกรีต", language="th")

# Search with category filter
steel_results = search_materials(
    client,
    "rebar",
    category_filter="Steel",
    limit=10
)

# Regex search (all materials with "C30" in name)
results = search_materials(client, ".*C30.*")
```

---

### 3. list_materials_by_category()

List all materials in a specific category.

**Signature:**
```python
list_materials_by_category(
    client: GraphDBClient,
    category: str,
    language: str = "en",
    include_subcategories: bool = True,
    sort_by: str = "label",
    limit: Optional[int] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `client`: GraphDBClient instance
- `category`: Category name (e.g., "Concrete", "Steel", "Aluminum")
- `language`: Language for labels ("en" or "th")
- `include_subcategories`: If True, includes materials from subclasses via RDFS inference
- `sort_by`: Sort field ("label", "emission_factor", "effective_date")
- `limit`: Optional maximum number of results

**Returns:**
```python
[
    {
        'material_id': 'http://tgo.or.th/materials/concrete-c15',
        'label': 'Concrete C15',
        'type': 'http://tgo.or.th/ontology#Concrete',
        'category': 'Concrete',
        'emission_factor': Decimal('380.2'),
        'unit': 'kgCO2e/m³',
        'effective_date': '2026-01-01'
    },
    # ... more results
]
```

**Examples:**
```python
# List all concrete materials
concretes = list_materials_by_category(client, "Concrete")
for material in concretes:
    print(f"{material['label']}: {material['emission_factor']}")

# Sort by emission factor (ascending)
concretes = list_materials_by_category(
    client,
    "Concrete",
    sort_by="emission_factor"
)

# Get top 5 most recent
recent = list_materials_by_category(
    client,
    "Steel",
    sort_by="effective_date",
    limit=5
)

# Thai labels
concretes_th = list_materials_by_category(
    client,
    "Concrete",
    language="th"
)
```

---

### 4. get_all_categories()

Retrieve all available material categories with counts.

**Signature:**
```python
get_all_categories(client: GraphDBClient) -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {'category': 'Concrete', 'count': 45},
    {'category': 'Steel', 'count': 23},
    {'category': 'Aluminum', 'count': 12},
    # ... more categories
]
```

**Example:**
```python
categories = get_all_categories(client)
print("Available material categories:")
for cat in categories:
    print(f"  {cat['category']}: {cat['count']} materials")

# Output:
# Available material categories:
#   Concrete: 45 materials
#   Steel: 23 materials
#   Aluminum: 12 materials
```

---

### 5. find_stale_materials()

Find materials with emission factors older than a threshold.

**Signature:**
```python
find_stale_materials(
    client: GraphDBClient,
    threshold_months: int = 6
) -> List[Dict[str, Any]]
```

**Parameters:**
- `client`: GraphDBClient instance
- `threshold_months`: Age threshold in months (default: 6)

**Returns:**
```python
[
    {
        'material_id': 'http://tgo.or.th/materials/concrete-c20-old',
        'label': 'Concrete C20',
        'category': 'Concrete',
        'emission_factor': Decimal('410.5'),
        'effective_date': '2025-06-01',
        'age_days': 273
    },
    # ... more stale materials
]
```

**Example:**
```python
# Find materials older than 6 months
stale = find_stale_materials(client, threshold_months=6)

print(f"Found {len(stale)} stale materials:")
for material in stale:
    print(f"  {material['label']}: {material['age_days']} days old")

# Find materials older than 1 year
very_stale = find_stale_materials(client, threshold_months=12)
```

---

## Utility Functions

### parse_bindings()

Parse SPARQL query result bindings into a simplified format.

```python
results = client.query("SELECT ?material ?label WHERE { ... }")
parsed = parse_bindings(results['results']['bindings'])

for item in parsed:
    print(item['material'], item['label'])
```

### extract_decimal_value()

Extract a decimal value from a SPARQL binding with type safety.

```python
binding = {'emissionFactor': {'value': '445.6'}}
emission_factor = extract_decimal_value(binding, 'emissionFactor')
# Returns: Decimal('445.6')
```

### extract_language_literal()

Extract a language-tagged literal from a SPARQL binding.

```python
binding = {'label': {'value': 'Concrete', 'xml:lang': 'en'}}
label_en = extract_language_literal(binding, 'label', 'en')
# Returns: 'Concrete'
```

---

## Error Handling

The library defines two custom exceptions:

### MaterialNotFoundError

Raised when a material URI is not found in the knowledge graph.

```python
try:
    result = get_emission_factor(client, "http://tgo.or.th/materials/nonexistent")
except MaterialNotFoundError as e:
    print(f"Material not found: {e}")
```

### QueryError

Raised when a SPARQL query fails (network error, malformed query, etc.).

```python
try:
    results = search_materials(client, "concrete")
except QueryError as e:
    print(f"Query failed: {e}")
```

---

## Best Practices

### 1. Use Decimal for Emission Factors

The library uses Python's `Decimal` type for emission factors to maintain precision.

```python
result = get_emission_factor(client, material_id)

# Correct: Use Decimal for calculations
total_emissions = result['emission_factor'] * Decimal('100.5')

# Avoid: Converting to float loses precision
# total_emissions = float(result['emission_factor']) * 100.5
```

### 2. Handle Bilingual Labels

Always consider both English and Thai labels for Thai construction projects.

```python
result = get_emission_factor(client, material_id)

# Display both languages
print(f"Material: {result['label_en']} ({result['label_th']})")
```

### 3. Check Data Staleness

Regularly check for stale emission factors and warn users.

```python
stale = find_stale_materials(client, threshold_months=6)

if stale:
    print(f"WARNING: {len(stale)} materials have outdated emission factors")
    for material in stale[:5]:  # Show first 5
        print(f"  - {material['label']} ({material['age_days']} days old)")
```

### 4. Category Filtering

Use category filters to narrow searches and improve performance.

```python
# Faster: Search within specific category
concrete_results = search_materials(
    client,
    "C30",
    category_filter="Concrete"
)

# Slower: Search all categories
all_results = search_materials(client, "C30")
```

---

## Integration Examples

### BOQ Material Matching

```python
def match_boq_item_to_tgo(client, boq_item_name):
    """Match a BOQ item to a TGO material."""
    # Try exact search first
    results = search_materials(client, boq_item_name, limit=5)

    if not results:
        # Fallback: extract keywords and search
        keywords = extract_keywords(boq_item_name)
        results = search_materials(client, keywords[0], limit=10)

    return results

# Usage
boq_item = "Ready-mixed Concrete Grade 30"
matches = match_boq_item_to_tgo(client, boq_item)

if matches:
    best_match = matches[0]
    print(f"Matched to: {best_match['label']}")
    print(f"Emission factor: {best_match['emission_factor']} {best_match['unit']}")
```

### Carbon Calculation

```python
from decimal import Decimal

def calculate_material_carbon(client, material_id, quantity, unit):
    """Calculate total carbon emissions for a material quantity."""
    result = get_emission_factor(client, material_id, include_metadata=True)

    # Check data quality
    if result['metadata']['data_quality'] != 'Verified':
        print(f"Warning: Using {result['metadata']['data_quality']} data")

    # Calculate emissions
    emissions = result['emission_factor'] * Decimal(str(quantity))

    # Apply uncertainty range
    uncertainty = result['metadata'].get('uncertainty', Decimal('0'))
    lower_bound = emissions * (1 - uncertainty)
    upper_bound = emissions * (1 + uncertainty)

    return {
        'emissions': emissions,
        'uncertainty_range': (lower_bound, upper_bound),
        'unit': result['unit'],
    }

# Usage
carbon = calculate_material_carbon(
    client,
    "http://tgo.or.th/materials/concrete-c30",
    quantity=150.5,  # m³
    unit="m³"
)

print(f"Total emissions: {carbon['emissions']} {carbon['unit']}")
print(f"Range: {carbon['uncertainty_range'][0]} - {carbon['uncertainty_range'][1]}")
```

### Dashboard Statistics

```python
def get_material_statistics(client):
    """Generate statistics for dashboard."""
    categories = get_all_categories(client)
    stale = find_stale_materials(client, threshold_months=6)

    total_materials = sum(cat['count'] for cat in categories)

    return {
        'total_materials': total_materials,
        'total_categories': len(categories),
        'stale_count': len(stale),
        'top_categories': categories[:5],
    }

# Usage
stats = get_material_statistics(client)
print(f"Total materials: {stats['total_materials']}")
print(f"Stale materials: {stats['stale_count']}")
print(f"Top categories: {[c['category'] for c in stats['top_categories']]}")
```

---

## Performance Optimization

### 1. Use Limits for Large Result Sets

```python
# Good: Limit results for UI display
results = search_materials(client, "concrete", limit=20)

# Avoid: Fetching all results if only showing first 20
results = search_materials(client, "concrete")[:20]
```

### 2. Cache Category Lists

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_cached_categories(client_url):
    """Cache category list for 1 hour."""
    client = GraphDBClient(client_url)
    return get_all_categories(client)
```

### 3. Batch Queries When Possible

```python
# Instead of multiple individual queries:
for material_id in material_ids:
    result = get_emission_factor(client, material_id)

# Use a single SPARQL query with VALUES clause:
query = f"""
SELECT ?material ?emissionFactor ?unit
WHERE {{
    VALUES ?material {{ <{material_ids[0]}> <{material_ids[1]}> ... }}
    ?material tgo:hasEmissionFactor ?emissionFactor ;
              tgo:hasUnit ?unit .
}}
"""
results = client.query(query)
```

---

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/core/knowledge_graph/test_sparql_queries.py

# Run specific test class
pytest tests/core/knowledge_graph/test_sparql_queries.py::TestGetEmissionFactor

# Run with coverage
pytest --cov=core.knowledge_graph.sparql_queries tests/core/knowledge_graph/test_sparql_queries.py

# Run performance tests (requires real GraphDB data)
pytest tests/core/knowledge_graph/test_sparql_queries.py::TestPerformance --runperformance
```

---

## Troubleshooting

### Connection Issues

```python
from core.knowledge_graph import GraphDBError

try:
    client = GraphDBClient("http://localhost:7200/repositories/carbonbim-thailand")
    client.test_connection()
except GraphDBError as e:
    print(f"Connection failed: {e}")
    # Check: Is GraphDB running? Is the repository name correct?
```

### No Results Found

```python
results = search_materials(client, "concrete")

if not results:
    # Possible causes:
    # 1. No data loaded in GraphDB
    # 2. Wrong language parameter
    # 3. Too specific search query

    # Try broader search
    results = search_materials(client, ".*", limit=10)  # Get any 10 materials
```

### Precision Issues

```python
# Always use Decimal for emission factor calculations
from decimal import Decimal

# Correct
quantity = Decimal('100.5')
factor = Decimal('445.6')
total = quantity * factor

# Wrong (loses precision)
quantity = 100.5
factor = 445.6
total = quantity * factor  # May have floating-point errors
```

---

## Version History

- **v1.0.0** (2026-03-22): Initial release
  - Basic query functions
  - Bilingual support
  - RDFS inference
  - Decimal precision for emission factors
  - Comprehensive test suite

---

## License

See project LICENSE file.

---

## Support

For issues or questions, contact the BKS cBIM AI Platform team.
